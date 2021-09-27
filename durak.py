from enums import Enum, auto
from itertools import product
from random import shuffle
from time import sleep

class Color(Enum):
    HEARTS = auto()
    DIAMONDS = auto()
    SPADES = auto()
    CLUBS = auto()

class Number(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class Setting(Enum):
    CARDS = auto()
    FAIR = auto()
    TIE = auto()
    THROW_EVERYONE = auto()
    FORWARD = auto()

class CardAmount(Enum):
    SMALL = 24
    NORMAL = 36
    LARGE = 52

class Settings:
    def __init__(self):
        self.settings = {
            Setting.CARDS: CardAmount.NORMAL,
            Setting.FAIR: True,
            Setting.TIE: False,
            Setting.THROW_EVERYONE: True,
            Setting.FORWARD: True
        }

    def set(self, key: Setting, val):
        self.settings[key] = val

    def get(self, key: Setting):
        return self.settings[key]

    @staticmethod
    def fromvalues(cards: CardAmount, fair: bool, tie: bool, throw_everyone: bool, forward: bool):
        set = Settings()
        set.set(Setting.CARDS, cards)
        set.set(Setting.FAIR, fair)
        set.set(Setting.TIE, tie)
        set.set(Setting.THROW_EVERYONE, throw_everyone)
        set.set(Setting.FORWARD, forward)
        return set

class Card:
    number: Number
    color: Color
    def __init__(self, col, num, game):
        self.number = num
        self.color = col
        self.game = game

    def __eq__(self, card):
        return self.color == card.color and self.number == card.number

    def __le__(self, card):
        return not self.__gt__(card)

    def __lt__(self, card):
        return not self.__ge__(card)

    def __ge__(self, card):
        if self.color == card.color and self.number != card.number: return self.number.value > card.number.value
        elif self.color == self.game.cool and card.color != self.game.cool: return True
        elif self.color != self.game.cool and card.color == self.game.cool: return False
        elif self.color == card.color and self.number == card.nubmer: return True
        elif self.color != card.color: return self.number.value >= card.number.value
        else: return False

    def __gt__(self, card):
        if self.color == card.color and self.number != card.number: return self.number.value > card.number.value
        elif self.color == self.game.cool and card.color != self.game.cool: return True
        elif self.color != self.game.cool and card.color == self.game.cool: return False
        elif self.color == card.color and self.number == card.nubmer: return False
        elif self.color != card.color: return self.number.value > card.number.value
        else: return False

    def can_beat(self, card):
        if self.color == self.game.cool and card.color != self.game.cool: return True
        if self.color != self.game.cool and card.color == self.game.cool: return False
        else:
            if self.color != card.color: return False
            return self.number.value > card.number.value

    def __str__(self):
        pd = {
            "HEARTS": "Hearts", "SPADES": "Spades", "CLUBS": "Clubs", "DIAMONDS": "Diamonds",
            "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5, "SIX": 6, "SEVEN": 7, "EIGHT": 8,
            "NINE": 9, "TEN": 10, "JACK": "Jack", "QUEEN": "Queen", "KING": "King", "ACE": "Ace"
        }
        return f"{str(pd[self.number.name])} {pd[self.color.name]}"

    def __repr__(self):
        return f"<Card number={self.number}, color={self.color}>"

    def can_forward(self, card):
        return card.number == self.number

    @staticmethod
    def fromstring(string: str, game=None):
        rawc, rawn = string.strip().split()
        rawc, rawn = rawc.lower(), rawn.lower()
        cdict = {Color.HEARTS: ["hearts", "heart", "чирвы", "сердце", "чирва"], Color.DIAMONDS: ["diamond", "diamonds", "бубна"], Color.SPADES: ["spades", "spade", "пики", "пика"], Color.CLUBS: ["clubs", "club", "трефа", "крест"]}
        ndict = {"2": Number.TWO, "3": Number.THREE, "4": Number.FOUR, "5": Number.FIVE, "6": Number.SIX, "7": Number.SEVEN, "8": Number.EIGHT, "9": Number.NINE, "10": Number.TEN,
                 "j": Number.JACK, "jack": Number.JACK, "в": Number.JACK, "валет": Number.JACK, "валентин": Number.JACK,
                 "q": Number.QUEEN, "queen": Number.QUEEN, "д": Number.QUEEN, "дама": Number.QUEEN, "дима": Number.QUEEN,
                 "k": Number.KING, "king": Number.KING, "к": Number.KING, "король": Number.KING, "кирилл": Number.KING,
                 "a": Number.ACE, "ace": Number.ACE, "т": Number.ACE, "туз": Number.ACE, "тузик": Number.ACE}
        recc = None
        for k,v in cdict.items():
            for d in v:
                if rawc == d:
                    recc = k; break
            if recc: break
        else:
            raise ValueError("Invalid color '%s'" % rawc)

        if rawn in ndict: rnum = ndict[rawn]
        else: raise ValueError("Invalid number '%s'" % rawn)

        return Card(recc, rnum, game)

class AI:
    @staticmethod
    def move(deck: list[Card]) -> Card:
        return min(deck)

    @staticmethod
    def beat(deck: list[Card], card: Card) -> Card or None:
        possibles = []
        for i in deck:
            if i.can_beat(card): possibles.append(i)
        return None if not possibles else min(possibles)

class UnfairAI(AI):
    def __init__(self):
        super().__init__()

class Game:
    def __init__(self, players: list[str], settings: Settings = None):
        if len(players) < 2: raise ValueError("Not enough players (should be 2 or more)")
        _set = set(players)
        if(len(_set) != len(players)): raise ValueError("Duplicate names found in player list!")
        self.moving = players[0]
        self.cool = None
        if settings is None:
            self.settings = Settings()
        else:
            self.settings = settings
        if len(players) * 6 > self.settings.get(Setting.CARDS).value: raise ValueError("Too many players and too few cards.")
        self.decks = {x: [] for x in players}
        self.give_out_cards()

    def request(self, playername: str):
        return self.decks[playername]

    def give_out_cards(self):
        self.deck = self.gen_full_deck()
        for player in self.decks:
            for i in range(6):
                self.decks[player].append(self.take_card())
            self.decks[player].sort()

    def take_card(self):
        if len(self.deck) <= 0: return None
        return self.deck.pop(0)

    def gen_full_deck(self):
        amount = self.settings.get(Setting.CARDS)
        deck = []
        numbs = []
        for x in [Number.ACE, Number.KING, Number.QUEEN, Number.JACK, Number.TEN, Number.NINE]:
            numbs.append(x)
        if amount != CardAmount.SMALL:
            for x in [Number.EIGHT, Number.SEVEN, Number.SIX]: numbs.append(x)
        if amount == CardAmount.LARGE:
            for x in [Number.FIVE, Number.FOUR, Number.THREE, Number.TWO]: numbs.append(x)

        for x,y in product(numbs, list(Color)):
            deck.append(Card(y, x, self))

        shuffle(deck)
        self.cool = deck[-1].color
        return deck

    def popcard(self, name, card):
        self.decks[name].pop(self.decks[name].index(card))
        self.decks[name].sort()

    def next_player(self):
        players = list(self.decks.keys())
        ind = players.index(self.moving)
        ind += 1
        return players[ind] if len(players) > (ind) else players[0]

    def give_card(self, name, card):
        self.decks[name].append(card)
        self.decks[name].sort()

    def pass_move(self, took: bool = False):
        players = list(self.decks.keys())
        ind = players.index(self.moving)
        num = 1 if not took else 2
        ind += num
        self.moving = players[ind] if ( len(players)  + 1 - num ) > ind else players[0]

    def botgame(self):
        while True:
            put = AI.move(self.request(self.moving))
            print(self.moving + " puts a " + str(put))
            self.popcard(self.moving, put)
            beat = AI.beat(self.request(self.next_player()), put)
            print(self.next_player() + " beats with a " + str(beat))
            if beat:
                self.popcard(self.next_player(), beat)
                self.pass_move(False)
            else:
                self.give_card(self.next_player(), put)
                self.pass_move(True)
            sleep(1)

def test():
    set = Settings.fromvalues(CardAmount.NORMAL, True, True, True, True)
    game = Game(["ivan", "dimon", "petr", "vasya"], set)
    game.botgame()
    print("cool color is:", game.cool)
    print("deck of ivan is: ", end='')
    print(*[str(x) for x in game.request("ivan")], sep=', ')
    print("deck of dimon is: ", end='')
    print(*[str(x) for x in game.request("dimon")], sep=', ')
    card = AI.move(game.request("ivan"))
    print(card)
    beat = AI.beat(game.request("dimon"), card)
    print(beat)

if __name__ == '__main__':
    test()