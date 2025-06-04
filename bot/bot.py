import os
import ast
import random
import asyncio
import discord
from discord.ext import commands

from .tokenizer import SimpleTokenizer
from .memory import Memory
from .games import TicTacToeGame, RockPaperScissorsGame, GuessNumberGame, HangmanGame
from .tts import TextToSpeech
from .game_ai import GameAI
from .adventure import AdventureGame
from .dialogue import DialogueMemory
from .logger import Logger
from .utils import env_bool, env_list

# Choose your AI backend here. Replace with your own implementation.
# For demonstration, we use a placeholder function.

async def call_ai_model(prompt: str) -> str:
    """Placeholder AI call. Replace with your own model integration."""
    # In a real implementation, send `prompt` to your model (OpenAI, Llama, etc.)
    # and return the model's response.
    return f"Echo: {prompt}"

class ChatBot(commands.Cog):
    def __init__(self, bot: commands.Bot, tokenizer=None, name: str | None = None):
        self.bot = bot
        self.name = name
        self.tokenizer = tokenizer or SimpleTokenizer()
        self.personality = os.getenv(
            "BOT_PERSONALITY",
            "You are an entertaining and helpful assistant who may use mild swearing but never slurs."
        )

        self.siblings = env_list("BOT_SIBLINGS", "Alpha,Beta")
        self.sibling_personalities = {}
        for s in self.siblings:
            key = f"BOT_PERSONALITY_{s.upper()}"
            self.sibling_personalities[s] = os.getenv(key, self.personality)

        self.last_messages = {}

        # Persistent memory handler
        self.memory = Memory()

        # Active games per channel
        self.tictactoe_games = {}
        self.rps_games = {}
        self.guess_games = {}
        self.hangman_games = {}
        self.adventure_games = {}
        self.voice_clients = {}

        # Voice and TTS
        self.enable_tts = env_bool("ENABLE_TTS", True)
        self.tts = TextToSpeech(lang=os.getenv("TTS_LANG", "en"))

        # Logger and dialogue memory
        self.logger = Logger()
        self.dialogue = DialogueMemory()

        # Game AI stub
        self.game_ai = GameAI()

        # Cursing and slur filter configuration
        self.allowed_cuss = {"damn", "shit", "fuck"}
        # Replace with your own blocked terms; these are placeholders
        self.blocked_words = {"badslur1", "badslur2"}

    def cog_unload(self):
        self.memory.close()
        self.logger.log("Cog unloaded")

    # Utility methods
    def history(self, channel_id: int) -> str:
        return self.memory.history(channel_id)

    def update_history(self, channel_id: int, entry: str) -> None:
        self.memory.update_history(channel_id, entry)

    def filter_output(self, text: str) -> str:
        """Replace blocked words with [filtered] while allowing mild cussing."""
        tokens = text.split()
        out_tokens = []
        for t in tokens:
            word = t.lower().strip(".,!?")
            if word in self.blocked_words:
                out_tokens.append("[filtered]")
            else:
                out_tokens.append(t)
        return " ".join(out_tokens)

    def think(self, message: str) -> str | None:
        """Very small reasoning step for math expressions."""
        try:
            tree = ast.parse(message, mode="eval")
            if all(
                isinstance(
                    node,
                    (
                        ast.Expression,
                        ast.BinOp,
                        ast.UnaryOp,
                        ast.Num,
                        ast.Constant,
                        ast.operator,
                    ),
                )
                for node in ast.walk(tree)
            ):
                result = eval(compile(tree, filename="<ast>", mode="eval"))
                return str(result)
        except Exception:
            pass
        return None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        self.logger.log(f"Message from {message.author}: {message.content}")
        self.dialogue.add(message.author.id, "User", message.content)

        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return  # Let command processing handle it

        channel_id = message.channel.id

        # Learn from human-to-human conversations
        last = self.last_messages.get(channel_id)
        if last and last[0] != message.author.id:
            self.memory.add_training(last[1], message.content)
        if message.author != self.bot.user:
            self.last_messages[channel_id] = (message.author.id, message.content)

        # Only respond when mentioned or when this bot's name is in the text
        name_to_check = self.name.lower() if self.name else self.bot.user.name.lower()
        if not (
            self.bot.user in message.mentions
            or name_to_check in message.content.lower()
        ):
            return

        personality = self.sibling_personalities.get(self.name, self.personality)

        tokens = self.tokenizer.encode(message.content)
        prompt = self.tokenizer.decode(tokens)

        # Simple reasoning step (math evaluation)
        thought = self.think(prompt)
        if thought is not None:
            await message.channel.send(thought)
            self.update_history(channel_id, f"\nUser: {prompt}\nAssistant: {thought}")
            return

        history = self.history(channel_id)
        training = self.memory.training()
        if prompt in training:
            response = training[prompt]
        else:
            combined_prompt = f"{personality}\n{history}\nUser: {prompt}\nAssistant:"
            response = await call_ai_model(combined_prompt)

        filtered = self.filter_output(response)
        self.memory.add_training(prompt, response)
        await message.channel.send(filtered)
        if self.enable_tts:
            # If connected to a voice channel, speak the reply aloud
            if message.guild and message.guild.id in self.voice_clients:
                vc = self.voice_clients[message.guild.id]
                try:
                    path = self.tts.speak(filtered)
                    if vc.is_playing():
                        vc.stop()
                    vc.play(
                        discord.FFmpegPCMAudio(path),
                        after=lambda e: os.remove(path),
                    )
                except Exception:
                    pass
            # Also send the text as a private message
            try:
                await message.author.send(filtered)
            except Exception:
                pass
        self.update_history(channel_id, f"\nUser: {prompt}\nAssistant: {filtered}")
        self.logger.log(f"Response: {filtered}")
        self.dialogue.add(message.author.id, "Assistant", filtered)

    def reward(self, user_id: int, amount: int = 1):
        """Reward a user with points."""
        self.memory.add_reward(user_id, amount)

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send("Pong!")

    @commands.command()
    async def help(self, ctx: commands.Context):
        await ctx.send(
            "Available commands: /ping, /help, /train, /tictactoe, /move, /rps, /rpsmove, /guessnumber, /guess, /hangman, /hang, /adventure, /adv, /dm, /history, /clearhistory, /giftcookies, /cookies, /rewards, /join, /leave, /play"
        )

    @commands.command()
    async def train(self, ctx: commands.Context, prompt: str, response: str):
        """Store a simple training pair."""
        self.memory.add_training(prompt, response)
        await ctx.send("Training example stored.")

    @commands.command()
    async def tictactoe(self, ctx: commands.Context, opponent: discord.Member):
        channel = ctx.channel.id
        if channel in self.tictactoe_games:
            await ctx.send("A game is already in progress in this channel.")
            return
        self.tictactoe_games[channel] = TicTacToeGame(ctx.author.id, opponent.id)
        await ctx.send(
            f"TicTacToe started! {ctx.author.mention} vs {opponent.mention}. Use /move <0-8>."
        )

    @commands.command()
    async def move(self, ctx: commands.Context, position: int):
        channel = ctx.channel.id
        game = self.tictactoe_games.get(channel)
        if not game:
            await ctx.send("No active game in this channel.")
            return
        msg, result = game.make_move(ctx.author.id, position)
        if msg:
            await ctx.send(msg)
        if result == "END":
            winner_mark = game.check_winner()
            if winner_mark:
                winner_id = (
                    game.state.players[0] if winner_mark == "X" else game.state.players[1]
                )
                self.reward(winner_id)
            del self.tictactoe_games[channel]

    @commands.command()
    async def history(self, ctx: commands.Context, limit: int = 10):
        channel = ctx.channel.id
        hist = self.history(channel)
        entries = hist.strip().split("\n")[-2 * limit:]
        if entries:
            await ctx.send("\n".join(entries))
        else:
            await ctx.send("No history.")

    @commands.command()
    async def clearhistory(self, ctx: commands.Context):
        channel = ctx.channel.id
        self.memory.clear_history(channel)
        await ctx.send("History cleared.")

    @commands.command()
    async def rps(self, ctx: commands.Context, opponent: discord.Member, rounds: int = 3):
        channel = ctx.channel.id
        if channel in self.rps_games:
            await ctx.send("Rock Paper Scissors already running in this channel.")
            return
        self.rps_games[channel] = RockPaperScissorsGame(ctx.author.id, opponent.id, rounds)
        await ctx.send(
            f"RPS started! {ctx.author.mention} vs {opponent.mention}. Use /rpsmove <choice>."
        )

    @commands.command()
    async def rpsmove(self, ctx: commands.Context, choice: str):
        channel = ctx.channel.id
        game = self.rps_games.get(channel)
        if not game:
            await ctx.send("No active RPS game in this channel.")
            return
        if ctx.author.id == game.players[0]:
            game_choice = choice
            bot_choice = random.choice(RockPaperScissorsGame.CHOICES)
            result = game.play_round(game_choice, bot_choice)
            await ctx.send(f"You chose {game_choice}, bot chose {bot_choice}. {result}")
        else:
            await ctx.send("Only the game starter can play against the bot.")
        if game.state.current_round >= game.state.rounds:
            p1 = game.players[0]
            p2 = game.players[1]
            s1 = game.state.scores[p1]
            s2 = game.state.scores[p2]
            if s1 > s2:
                self.reward(p1)
            elif s2 > s1:
                self.reward(p2)
            del self.rps_games[channel]

    @commands.command()
    async def guessnumber(self, ctx: commands.Context, max_attempts: int = 5):
        """Start a number guessing game."""
        channel = ctx.channel.id
        if channel in self.guess_games:
            await ctx.send("GuessNumber already running in this channel.")
            return
        self.guess_games[channel] = GuessNumberGame(max_attempts)
        await ctx.send("Guess a number between 1 and 100 using /guess <num>.")

    @commands.command()
    async def guess(self, ctx: commands.Context, number: int):
        channel = ctx.channel.id
        game = self.guess_games.get(channel)
        if not game:
            await ctx.send("No active GuessNumber game.")
            return
        result = game.guess(number)
        await ctx.send(result)
        if "Correct" in result:
            self.reward(ctx.author.id)
        if "Correct" in result or "Out of attempts" in result:
            del self.guess_games[channel]

    @commands.command()
    async def dm(self, ctx: commands.Context, *, message: str):
        """Send yourself a private message from the bot."""
        try:
            await ctx.author.send(message)
            await ctx.send("DM sent.")
        except Exception:
            await ctx.send("Unable to send DM.")

    @commands.command()
    async def hangman(self, ctx: commands.Context, max_attempts: int = 6):
        """Start a hangman game."""
        channel = ctx.channel.id
        if channel in self.hangman_games:
            await ctx.send("Hangman already running in this channel.")
            return
        self.hangman_games[channel] = HangmanGame(max_attempts)
        game = self.hangman_games[channel]
        await ctx.send(f"Hangman started! {game.state.display()} Use /hang <letter>.")

    @commands.command()
    async def hang(self, ctx: commands.Context, letter: str):
        channel = ctx.channel.id
        game = self.hangman_games.get(channel)
        if not game:
            await ctx.send("No active Hangman game.")
            return
        result = game.guess(letter)
        await ctx.send(result)
        if "You win" in result:
            self.reward(ctx.author.id)
        if "Game over" in result or "You win" in result:
            del self.hangman_games[channel]

    @commands.command()
    async def adventure(self, ctx: commands.Context):
        """Start a tiny text adventure."""
        channel = ctx.channel.id
        if channel in self.adventure_games:
            await ctx.send("Adventure already running. Use /adv to play.")
            return
        self.adventure_games[channel] = AdventureGame()
        await ctx.send(self.adventure_games[channel].look())

    @commands.command()
    async def adv(self, ctx: commands.Context, *, command: str):
        game = self.adventure_games.get(ctx.channel.id)
        if not game:
            await ctx.send("No active adventure. Start with /adventure.")
            return
        result = game.handle_command(command)
        await ctx.send(result)
        if game.game_over:
            del self.adventure_games[ctx.channel.id]

    # Cookie and reward commands
    @commands.command()
    async def giftcookies(self, ctx: commands.Context, amount: int = 1):
        """Give the bot happiness cookies (server owner only)."""
        if not ctx.guild:
            await ctx.send("This command must be used in a server.")
            return
        if ctx.author.id != ctx.guild.owner_id:
            await ctx.send("Only the server owner can gift cookies.")
            return
        self.memory.add_cookies(ctx.guild.id, amount)
        total = self.memory.cookies(ctx.guild.id)
        await ctx.send(f"Yum! Thank you for {amount} cookies. Total: {total}")

    @commands.command()
    async def cookies(self, ctx: commands.Context):
        """Check how many cookies the bot has."""
        if not ctx.guild:
            await ctx.send("Use this in a server.")
            return
        total = self.memory.cookies(ctx.guild.id)
        await ctx.send(f"I currently have {total} cookies!")

    @commands.command()
    async def rewards(self, ctx: commands.Context):
        """Show your reward points."""
        points = self.memory.rewards(ctx.author.id)
        await ctx.send(f"You have {points} reward points.")

    # Voice channel commands
    @commands.command()
    async def join(self, ctx: commands.Context):
        """Join the voice channel of the command author."""
        if not ctx.author.voice:
            await ctx.send("You are not in a voice channel.")
            return
        if ctx.guild.id in self.voice_clients:
            await ctx.send("Already connected.")
            return
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        self.voice_clients[ctx.guild.id] = vc
        await ctx.send(f"Joined {channel.name}")

    @commands.command()
    async def leave(self, ctx: commands.Context):
        """Disconnect from the current voice channel."""
        vc = self.voice_clients.get(ctx.guild.id)
        if vc:
            await vc.disconnect()
            del self.voice_clients[ctx.guild.id]
            await ctx.send("Left the voice channel.")
        else:
            await ctx.send("Not connected to a voice channel.")

    @commands.command()
    async def play(self, ctx: commands.Context, file_path: str):
        """Play a local audio file in the current voice channel."""
        vc = self.voice_clients.get(ctx.guild.id)
        if not vc:
            await ctx.send("Join a voice channel first with /join.")
            return
        if not os.path.isfile(file_path):
            await ctx.send("Audio file not found.")
            return
        if vc.is_playing():
            vc.stop()
        source = discord.FFmpegPCMAudio(file_path)
        vc.play(source)
        await ctx.send(f"Playing {file_path}.")


async def run_single(token: str, sibling: str | None = None):
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="/", intents=intents)
    bot.add_cog(ChatBot(bot, name=sibling))
    await bot.start(token)


def main():
    tokens_env = os.getenv("DISCORD_TOKENS")
    if tokens_env:
        tokens = [t.strip() for t in tokens_env.split(",") if t.strip()]
    else:
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise RuntimeError("DISCORD_TOKEN or DISCORD_TOKENS must be set")
        tokens = [token]

    sibling_names = env_list("BOT_SIBLINGS", "Alpha,Beta")

    async def runner():
        tasks = []
        for i, token in enumerate(tokens):
            sibling = sibling_names[i] if i < len(sibling_names) else None
            tasks.append(run_single(token, sibling))
        await asyncio.gather(*tasks)

    asyncio.run(runner())

if __name__ == "__main__":
    main()
