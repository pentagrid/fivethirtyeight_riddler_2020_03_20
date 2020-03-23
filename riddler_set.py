from enum import Enum
from itertools import combinations
from multiprocessing import Pool
from random import Random

# This represents one of the four three valued parameters a SET card has
class SetTriple(Enum):
    First = 0
    Second = 1
    Third = 2

    def __int__(self):
        return self.value

    # this method computes the missing set element between this
    # value and another value
    def get_set(self, b):
        a = self.value
        b = b.value
        if a == b:
            return SetTriple(a)
        c = a + b
        if c == 1:
            return SetTriple(2)
        elif c == 2:
            return SetTriple(1)
        elif c == 3:
            return SetTriple(0)
        assert 0

    def match(self, b, c):
        a = self
        if (a.value == b.value) and (a.value == c.value):
            return 1
        elif (a.value != b.value) and (a.value != c.value) and (c.value != b.value):
            return 1
        return 0


# this class represents one SET card
class SetCard:
    # number of cards in a SET deck
    num_cards = 81
    # number of different parameters each card has
    num_sets = 4
    # the number of variations of each parameter
    set_size = 3

    # these are each parameter of the card
    number = SetTriple(0)
    color = SetTriple(0)
    shape = SetTriple(0)
    shading = SetTriple(0)

    # constructor for building a card object given an ID 0..80
    def __init__(self, card_id):
        assert(card_id < self.num_cards)
        assert(card_id >= 0)
        self.number = SetTriple(card_id % self.set_size)
        self.color = SetTriple((card_id // self.set_size) % self.set_size)
        self.shape = SetTriple((card_id // self.set_size // self.set_size) % self.set_size)
        self.shading = SetTriple((card_id // self.set_size // self.set_size // self.set_size) % self.set_size)

    # this method gets the unique numeric ID for the card 0..80
    def get_id(self):
        id = 0
        id = id + int(self.number)
        id = id + self.set_size * int(self.color)
        id = id + self.set_size * self.set_size * int(self.shape)
        id = id + self.set_size * self.set_size * self.set_size * int(self.shading)
        return id

    # this method decides if this card and two others form a Set
    def is_match(self, card_b, card_c):
        card_a = self
        result = 1
        result = result and card_a.number.match(card_b.number, card_c.number)
        result = result and card_a.color.match(card_b.color, card_c.color)
        result = result and card_a.shape.match(card_b.shape, card_c.shape)
        result = result and card_a.shading.match(card_b.shading, card_c.shading)
        return result

    # this method computes the card that would complete a set between this card and another
    def compute_set(self, card_b):
        card_a = self
        card_c = SetCard(0)
        card_c.color = card_a.color.get_set(card_b.color)
        card_c.number = card_a.number.get_set(card_b.number)
        card_c.shape = card_a.shape.get_set(card_b.shape)
        card_c.shading = card_a.shading.get_set(card_b.shading)
        return card_c

# This class represents the full deck of SET cards, out of the box
class SetDeck:
    cards = []
    def __init__(self):
        for card in range(0, SetCard.num_cards):
            self.cards.append(SetCard(card))


def has_sets(cards):
    result = 0
    size = len(cards)

    for i in range(0, size-2):
        for j in range(i+1, size-1):
            for k in range(j+1, size):
                if cards[k].is_match(cards[i], cards[j]):
                    result = 1
                    break
            if result:
                break
        if result:
            break
    return result


def remove_card(card, cards):
    cds = [cd for cd in cards if (card.get_id() == cd.get_id())]
    for cd in cds:
        cards.remove(cd)


# this function expects a two card hand, with the cards not yet removed from the deck
def question_a_inner(hand):
    # the conbinations library uses tuples which are annoying in this case
    hand = list(hand)
    # create a fresh deck without these two cards in it
    cds = SetDeck().cards
    remove_card(hand[0], cds)
    remove_card(hand[1], cds)

    # remove the card we know will complete a set from the deck
    new_card = hand[0].compute_set(hand[1])
    remove_card(new_card, cds)

    while 1:
        # add a card from the deck
        new_card = cds[0]
        cds.remove(cds[0])
        # remove all the new sets completion cards from the deck
        for cd in hand:
            if len(cds) == 0:
                break
            remove_card(new_card.compute_set(cd), cds)
        hand.append(new_card)
        if len(cds) == 0:
            break
    return len(hand)


def question_a():
    # The algorithm starts with all combinations of 2 cards an 81 card deck.
    # It then uses the fact we can compute the set making card for each pair directly
    # to systematically remove cards from the deck that would create sets if drawn,
    # while then adding a new card that won't create a set and repeating the process until
    # the deck is empty.
    dk = SetDeck()
    cds = dk.cards
    results = []
    # compute initial hands of two cards
    hands = list(combinations(cds, 2))
    # let the computer cores work on each initial possible hand with the systematic deck reduction
    with Pool(8) as p:
        results.append(p.map(question_a_inner, hands))
    return max(results[0])


random = Random()
random.seed()


def pick_n(n, random):
    hand = []
    cds = SetDeck().cards
    while n > 0:
        n = n - 1
        i = random.randrange(0, len(cds))
        hand.append(cds[i])
        cds.remove(cds[i])
    return hand


def question_c_inner(ignore):
    global random
    return has_sets(pick_n(12, random))


def question_c():
    found = 0
    total = 0
    m = 1000
    c = 100
    for i in range(0, c):
        results = []
        random.seed()
        with Pool(10) as p:
            results.append(p.map(question_c_inner, range(0, m)))
        found = found + sum(results[0])
        total = total + len(results[0])

    return found / total


def add_card_from_deck(hand, deck, i):
    hand.append(deck[i])
    deck.remove(deck[i])
    if has_sets(hand):
        return len(hand) - 1
    else:
        results = []
        for j in range(0, len(deck) - 1):
            results.append(add_card_from_deck(hand.copy(), deck.copy(), j))
        return max(results)

if __name__ == '__main__':
    print("Question A Solution: " + str(question_a()))
    print("Question C Solution: " + str(question_c()))
