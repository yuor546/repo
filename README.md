# Custom Tokenizer Discord Chatbot

This repository contains a minimal example of a Discord chatbot that uses a
custom tokenizer. You can easily swap in your own tokenizer and AI backend.
The bot is implemented with `discord.py` and aims to be extensible for
additional features such as moderation or logging. By default it tries to be
generally entertaining in its responses.

The included `call_ai_model` function loads a tiny Markov chain model so the bot
can operate without any external service. You may replace it with your own model
integration so the bot can run entirely on your own AI stack.

## Architecture Overview

1. **Message Reception**: The bot listens to Discord events using
   `discord.py`. When a new message arrives, it checks whether the message is a
   command or regular text.
2. **Tokenization**: Incoming text is passed through a configurable tokenizer
   (`bot/tokenizer.py`). You may replace this with your own implementation.
3. **AI Model Call**: The processed text is sent to the AI backend
   (`call_ai_model`). This function can call any model API (OpenAI, local
   Llama, etc.) and returns the model's response.
4. **Response Delivery**: The response text is posted back to the Discord
   channel. Basic conversation history is stored per channel to maintain
   context.

```
Discord -> Tokenizer -> AI Model -> Discord
```

## Credits

This project was inspired by Vedal's **Neuro-sama**. The code here is a small
educational example and not affiliated with the original creator. Feel free to
extend it with your own ideas.

## Future Work

Possible extensions include adding real language model calls, more sophisticated
game logic, and richer voice synthesis. Contributions are welcome.

---

This repository is provided for demonstration purposes. Use at your own risk
and make sure to follow Discord's terms of service when deploying a bot.

## Sample Usage

```bash
# Install dependencies
pip install -r requirements.txt
# On Linux you may need the `ffmpeg` package for voice playback
# Speech transcription via `/transcribe` requires the `SpeechRecognition` package
# Voice recognition needs the `librosa` and `soundfile` packages
# Training the optional LSTM model requires the `tensorflow` package

# Set the Discord token in the environment (single bot)
export DISCORD_TOKEN="YOUR_BOT_TOKEN"
# Or run two sibling bots with separate tokens
# export DISCORD_TOKENS="TOKEN_FOR_VIVI,TOKEN_FOR_VEX"

# Optionally set a personality prompt
export BOT_PERSONALITY="You are an entertaining assistant."
# Optional comma-separated names for two siblings
export BOT_SIBLINGS="Vivi,Vex"

# You can also place these variables in a `.env` file and `source .env`
# before launching the bot. A sample `.env.example` is included.

# Run the bot
python -m bot.bot
# Make sure to run this command from the repository root. Running it from
# inside the `bot/` directory will cause an `ImportError` because the package
# cannot be located.
```

For two sibling bots named **Vivi** and **Vex**, place both tokens in the
`DISCORD_TOKENS` variable before running:

```bash
export DISCORD_TOKENS="TOKEN_FOR_VIVI,TOKEN_FOR_VEX"
export BOT_SIBLINGS="Vivi,Vex"
python -m bot.bot
```

When both bots share a channel they can hold short conversations without user input.

The bot supports simple slash-style commands like `/ping`, `/help`, `/tictactoe`, `/rps`, `/converse`, and history commands in
 addition to responding when it is mentioned by name or `@`. It can also join a voice channel and play a local audio file.

## Customizing the Tokenizer

Edit `bot/tokenizer.py` or create your own tokenizer class with `encode` and
`decode` methods. For example, you could implement emoji-based tokenization or
integrate a third-party library.

Update `bot/bot.py` to pass your tokenizer instance when creating the
`ChatBot` cog:

```python
from my_tokenizer import MyTokenizer
bot.add_cog(ChatBot(bot, tokenizer=MyTokenizer()))
```

## Changing the AI Backend

The `call_ai_model` function in `bot/bot.py` is a placeholder. Replace its
implementation with a call to your preferred model. For example, to use the
OpenAI API:

```python
import openai

async def call_ai_model(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )
    return response["choices"][0]["message"]["content"]
```

If you want to swap in a local model such as Llama, you can modify the
function to invoke that model instead.

### Training the Sample Markov Model

The repository includes a toy Markov chain implementation that can run
without any external APIs. Train it using your stored conversation pairs:

```bash
python -m bot.train_markov
```

This generates `markov_model.pkl`, which `bot/bot.py` loads automatically.
The model learns from the examples collected with `/train` and from observed
conversations, so you can improve it over time.

### Training a Small LSTM Model

For a more capable local model you can train a small character-level LSTM.
It learns from the same stored conversation pairs and saves a Keras model
(`lstm_model.h5`) plus vocabulary file (`lstm_vocab.pkl`):

```bash
python -m bot.train_lstm
```

If these files exist the bot will load the LSTM model instead of the Markov
chain when generating replies.

### Deep Training from Discord

To retrain the LSTM model without leaving Discord, run the `/deeptrain` command
in any channel the bot can access:

```bash
/deeptrain
```

This invokes the same process as running `python -m bot.train_lstm` locally and
reloads the updated model when finished.

## Extensibility

The current implementation is intentionally lightweight. You can add more
`discord.py` cogs for features like moderation, logging, or additional
commands. Because the tokenizer and AI backend are decoupled, it is easy to
experiment with new approaches without rewriting the bot.

## Extended Capabilities

This example demonstrates additional features beyond simple tokenization:

- **Persistent Memory**: Conversation history is saved per channel using Python's `shelve` module so the bot remembers context across restarts.
- **Training Samples**: Users can provide paired prompts and responses with the `/train` command to influence future replies.
- **Automatic Learning**: Every conversation is stored as a new training pair so the bot gradually adapts.
- **Thought Process**: Before calling the AI model the bot performs a lightweight reasoning step that can be customized.
- **Math Mode**: Messages that contain arithmetic expressions are evaluated locally for quick answers.
- **Tic‑Tac‑Toe**: The bot can host a game of tic‑tac‑toe between two users using the `/tictactoe` command.
- **Rock Paper Scissors**: Challenge the bot with `/rps` and make moves with `/rpsmove`.
- **History Commands**: Use `/history` to show recent conversation and `/clearhistory` to wipe it.
- **Voice Chat**: Use `/join` and `/leave` to manage voice connections and `/play` to stream a local file.
- **Voice Transcription**: Attach an audio file and use `/transcribe` to convert speech to text.
- **Voice Recognition**: Register your voice with `/registervoice` and identify speakers with `/identifyvoice`.
- **Cookies**: Server owners can gift the bot happiness cookies via `/giftcookies`.
- **Rewards**: Win games to earn reward points and view them with `/rewards`.
- **Sibling Chat**: Use `/converse` to watch the sibling bots talk to each other for a few rounds. They will also naturally reply to one another when sharing a channel, up to a few messages each time.
- **Deep Training Command**: Kick off LSTM training from Discord with `/deeptrain`.
- **Language Filter**: The bot allows mild swearing but will replace any blocked terms with `[filtered]`.
- **Entertaining Personality**: Responses aim to be playful and amusing.
- **Learning Mode**: The bot stores its replies as training data and even
  observes conversations between other users to expand its knowledge.
- **Mentions**: It only answers when mentioned by name or via `@`, allowing it
  to sit quietly until called upon.
- **Sibling Personalities**: Two AI siblings can be configured with the
  `BOT_SIBLINGS` environment variable (default `Vivi,Vex`). Each sibling can
  have its own personality prompt using `BOT_PERSONALITY_VIVI` and
  `BOT_PERSONALITY_VEX`. Provide matching tokens with
  `DISCORD_TOKENS="TOKEN_FOR_VIVI,TOKEN_FOR_VEX"` to run them as separate bot
  accounts from the same codebase.

These capabilities are intentionally simple but illustrate how the bot can be extended in many directions.

### Configurable Thought Step

The `think` method in `bot/bot.py` shows a basic chain‑of‑thought implementation. You can modify this function to add planning or tool use before the final model call.

### Example Training

```bash
# Teach the bot a custom reply
/train "Hello" "Hi there!"
```

Training samples are stored in the memory database and included in the prompt whenever the user message matches a trained example.

## Voice Commands

Use `/join` to have the bot connect to your current voice channel. `/play <file>` will play a local audio file and `/leave` disconnects the bot. Attach an audio file and use `/transcribe` to convert it to text. `/registervoice` saves your voice for recognition and `/identifyvoice` attempts to match a new sample to a registered user.

## Moderating Language

The bot's responses are passed through a small filter that replaces banned words with `[filtered]`. The list of blocked terms is defined in `bot/bot.py` and can be customized. Mild swearing such as "damn" or "shit" is allowed, but any slurs you add to the blocklist will be sanitized, e.g.:

```
shut up you stupid [filtered]
```

You can modify `allowed_cuss` and `blocked_words` in the `ChatBot` class to suit your own needs.

## Running Tests

Compile the modules to verify there are no syntax errors:

```bash
python -m py_compile \
    bot/tokenizer.py bot/bot.py bot/memory.py bot/games.py \
    bot/tts.py bot/stt.py bot/game_ai.py bot/adventure.py bot/dialogue.py \
    bot/logger.py bot/utils.py
```

## Text-to-Speech and DMs

Set `ENABLE_TTS=true` to have the bot read its replies aloud in a voice channel
using `gTTS`. Install the `gTTS` Python package and make sure `ffmpeg` is
available. If a voice connection exists it will stream the generated audio and
also send the text as a private message to the user who triggered it.

## Speech Recognition

Install the `SpeechRecognition` Python package and use `/transcribe` with an
audio attachment to convert speech into text. The bot uses the offline Sphinx
engine by default.

## Guess Number Game

Use `/guessnumber` to start a simple guessing game and `/guess` to make moves.

## Hangman

Start a hangman match with `/hangman`. Guess letters using `/hang` until you
either reveal the word or run out of attempts.

## Text Adventure

Begin a mini text adventure with `/adventure` and interact using `/adv`.

## Cookies and Rewards

Server owners can boost the bot's happiness by gifting **cookies**:

```bash
/giftcookies 5
```

Check the current cookie count with `/cookies`.

When you win certain games (TicTacToe, RPS, GuessNumber, Hangman) you earn
reward points. View your balance with `/rewards`.

## Logging and Dialogue Memory

Every message and response is recorded to `bot.log` via the `Logger` class, and
`DialogueMemory` keeps short histories per user for summaries.

## Game AI Stub

`bot/game_ai.py` contains a placeholder class for a separate AI model that could
control in-game actions, mirroring how Neuro-sama relies on a dedicated system
for gameplay.

You can mimic Neuro-sama and her "Evil" twin by setting
`BOT_SIBLINGS="Neuro,Evil"` and providing different personality prompts for each
with `BOT_PERSONALITY_NEURO` and `BOT_PERSONALITY_EVIL`.

## Inspiration from Neuro-sama

The voice features are inspired by **Neuro-sama**, an AI VTuber created by
`vedal987` that speaks with a high-pitched voice. Our bot can likewise speak in
voice chat while also sending text responses.

## Updated Tests

Run compilation to ensure the new modules are error free:

```bash
python -m py_compile \
    bot/tokenizer.py bot/bot.py bot/memory.py bot/games.py \
    bot/tts.py bot/stt.py bot/game_ai.py bot/adventure.py bot/dialogue.py \
    bot/logger.py bot/utils.py
```

