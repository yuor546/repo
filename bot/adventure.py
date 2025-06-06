from dataclasses import dataclass, field

@dataclass
class Room:
    name: str
    description: str
    exits: dict[str, str]
    items: list[str] = field(default_factory=list)

@dataclass
class Player:
    location: str = 'start'
    inventory: list[str] = field(default_factory=list)

class AdventureGame:
    """Very small text adventure with a few rooms."""

    def __init__(self):
        self.rooms = {
            'start': Room(
                name='start',
                description='You are in a small room. Exits lead east and south.',
                exits={'east': 'hall', 'south': 'closet'},
                items=['key'],
            ),
            'hall': Room(
                name='hall',
                description='A long hallway. There is a locked door to the north.',
                exits={'west': 'start', 'north': 'treasure'},
            ),
            'closet': Room(
                name='closet',
                description='A dusty closet filled with cobwebs.',
                exits={'north': 'start'},
            ),
            'treasure': Room(
                name='treasure',
                description='A glittering treasure room!',
                exits={'south': 'hall'},
                items=['treasure'],
            ),
        }
        self.player = Player()
        self.game_over = False

    def current_room(self) -> Room:
        return self.rooms[self.player.location]

    def look(self) -> str:
        room = self.current_room()
        desc = room.description
        if room.items:
            desc += '\nYou see: ' + ', '.join(room.items)
        desc += '\nExits: ' + ', '.join(room.exits.keys())
        return desc

    def move(self, direction: str) -> str:
        room = self.current_room()
        if direction not in room.exits:
            return 'You cannot go that way.'
        dest = room.exits[direction]
        if dest == 'treasure' and 'key' not in self.player.inventory:
            return 'The door is locked.'
        self.player.location = dest
        if dest == 'treasure':
            self.game_over = True
            return 'You found the treasure and win!'
        return self.look()

    def take(self, item: str) -> str:
        room = self.current_room()
        if item not in room.items:
            return 'There is no such item here.'
        room.items.remove(item)
        self.player.inventory.append(item)
        return f'You picked up {item}.'

    def handle_command(self, command: str) -> str:
        parts = command.split()
        if not parts:
            return 'Try a command.'
        action = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ''
        if action == 'look':
            return self.look()
        if action == 'move':
            return self.move(arg)
        if action == 'take':
            return self.take(arg)
        return 'Unknown command.'

