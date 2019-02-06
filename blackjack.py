from random import shuffle

from enum import Enum, unique


def sum_cards(cards):
    total = 0
    for card in reversed(sorted(cards, key=lambda c: c.value)):
        if card.type == Card.CardType.ACE:
            if total > 10:
                total += 1
            else:
                total += 11
        else:
            total += card.value
    return total

def is_hand_blackjack(hand):
    if len(hand) > 2:
        return False
    if Card.CardType.ACE in hand and (Card.CardType.TEN in hand or
                                      Card.CardType.KING in hand or
                                      Card.CardType.QUEEN in hand or
                                      Card.CardType.JACK in hand):
        return True
    return False


class Card:

    @unique
    class CardType(Enum):
        ACE='ACE'
        TWO='TWO'
        THREE='THREE'
        FOUR='FOUR'
        FIVE='FIVE'
        SIX='SIX'
        SEVEN='SEVEN'
        EIGHT='EIGHT'
        NINE='NINE'
        TEN='TEN'
        KING='KING'
        QUEEN='QUEEN'
        JACK='JACK'

    def __init__(self, card_type, value):
        self.type = card_type
        self.value = value

    def __str__(self):
        return f'{self.type.value}'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.type == other.type


class Player:
    """
    Represents a player or dealer. Keeps track of the player's hand.
    """

    def __init__(self, name):
        self.name = name
        self.hand = []

    def deal_initial_cards(self, card1, card2):
        if self.hand:
            raise Exception("Cannot deal initial cards when player's hand is not empty")
        self.hand.append(card1)
        self.hand.append(card2)

    def hit(self, card):
        self.hand.append(card)

    def is_bust(self):
        return sum_cards(self.hand) > 21


class Deck:
    """
    Represents a deck of cards. Initializes to a shuffled deck.
    """

    def __init__(self, num_decks=2):
        self.cards = [Card(Card.CardType.ACE, 1),
                      Card(Card.CardType.TWO, 2),
                      Card(Card.CardType.THREE, 3),
                      Card(Card.CardType.FOUR, 4),
                      Card(Card.CardType.FIVE, 5),
                      Card(Card.CardType.SIX, 6),
                      Card(Card.CardType.SEVEN, 7),
                      Card(Card.CardType.EIGHT, 8),
                      Card(Card.CardType.NINE, 9),
                      Card(Card.CardType.TEN, 10),
                      Card(Card.CardType.KING, 10),
                      Card(Card.CardType.QUEEN, 10),
                      Card(Card.CardType.JACK, 10)] * num_decks
        shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop()


class BlackJack:
    """
    Maintains the global state of the game.

    When the object is created, the first 2 cards have been dealt to the players and the dealer.
    It's the a player's turn to either hit till he goes bust or stand.

    At this point, the following methods can be called:
        - get_current_player_name()
            Gets the name of the player whose turn it is.
        - hit_current_player()
            Choose the HIT option for the current player.
            A bust makes it the next player's turn.
        - stand_current_player()
            Chose the STAND option for the current player.
            Always makes it the next player's turn.

    Either choice makes it the next player's turn to do the same.
    If there is no next player (the last player has had his turn), the dealer deals himself
    cards till the game finishes.

    The `get_game_state_str()` can be called at any time to get a text representation of the
    game's state, i.e, all the players' status and hands.

    The `game_finished()` function can be called to test if the game is in finished state of not.
    Any call to hit_current_player() or stand_current_player() may result in the game being
    finished, so this check should be done after every call of these methods.

    When the game is finished, the `get_game_result_str()` method can be used to get a string
    representation of the result of each player.
    """

    def __init__(self, player_names, deck=None):
        assert player_names, 'At least one player is required.'
        self._players = [Player(name) for name in player_names]
        self._dealer = Player('Dealer')
        if deck is None:
            self._deck = Deck(num_decks=2)
        else:
            self._deck = deck
        # When this is None, it means the game has ended.
        self._current_player = self._players[0]

        for player in self._players + [self._dealer]:
            player.deal_initial_cards(self._deck.draw_card(), self._deck.draw_card())

    def get_current_player_name(self):
        assert self._current_player is not None, "Game has ended."
        return self._current_player.name

    def hit_current_player(self):
        assert self._current_player is not None, "Game has ended."
        self._current_player.hit(self._deck.draw_card())
        if self._current_player.is_bust():
            self._next_player()

    def stand_current_player(self):
        assert self._current_player is not None, "Game has ended."
        self._next_player()

    def _next_player(self):
        assert self._current_player is not None, "Game has ended."
        curr_player_index = self._players.index(self._current_player)
        if curr_player_index == len(self._players) - 1:
            self._play_dealers_turn()
            self._current_player = None
        else:
            self._current_player = self._players[curr_player_index + 1]

    def game_finished(self):
        return self._current_player is None

    def _play_dealers_turn(self):
        while sum_cards(self._dealer.hand) < 17:
            self._dealer.hit(self._deck.draw_card())

    def get_game_state(self):
        state = {'finished': self.game_finished(),
                 'current_player': None if self.game_finished() else self._current_player.name,
                 'players': {p.name: {'hand': p.hand,
                                      'bust': p.is_bust()}
                             for p in self._players},
                 'dealer': {'hand': self._dealer.hand,
                            'bust': self._dealer.is_bust()}}
        return state

    def _player_str(self, name, hand, is_bust):
        cards_str = ', '.join(str(c) for c in hand)
        player_str = f"{name} ({'BUST' if is_bust else sum_cards(hand)}):\n\t{cards_str}"
        return player_str

    def _dealer_str(self, hand, is_bust, show_hole=True):
        cards_str = ', '.join(str(c) for c in self._dealer.hand) if show_hole else f"{self._dealer.hand[0]}, X"
        dealer_str = f"Dealer ({'BUST' if self._dealer.is_bust() else sum_cards(self._dealer.hand) if show_hole else 'X'}):\n\t{cards_str}"
        return dealer_str

    def get_game_state_str(self, show_hole=True):
        state = self.get_game_state()
        player_strings = [self._player_str(name, p_state['hand'], p_state['bust'])
                          for name, p_state in state['players'].items()]
        dealer = state['dealer']
        player_strings.append(self._dealer_str(dealer['hand'], dealer['bust'], show_hole))
        return '\n\n'.join(player_strings)

    def get_game_result(self):
        assert self._current_player is None, "Game has not ended yet."
        player_results = {}
        for player in self._players:
            result = None
            if player.is_bust():
                result = 'BUST'
            elif self._dealer.is_bust():
                result = 'WON'
            else:
                player_hand_sum = sum_cards(player.hand)
                dealer_hand_sum = sum_cards(self._dealer.hand)
                if player_hand_sum > dealer_hand_sum:
                    result = 'WON'
                elif dealer_hand_sum > player_hand_sum:
                    result = 'LOST'
                else:
                    if is_hand_blackjack(player.hand) and is_hand_blackjack(self._dealer.hand):
                        result = 'PUSH'
                    elif is_hand_blackjack(player.hand):
                        result = 'WON'
                    elif is_hand_blackjack(self._dealer.hand):
                        result = 'LOST'
                    else:
                        # Non-blackjack hands equaling the same points
                        result = 'PUSH'
            assert result is not None
            player_results[player.name] = result
        return player_results

    def get_game_result_str(self):
        player_results = self.get_game_result()
        return "\n".join(f'{name}: {result}' for name, result in player_results.items())


def play_blackjack():
    players = []
    while True:
        name = input("Enter player name: ")
        if not name:
            print("Blank name not allowed, please try again.")
        else:
            players.append(name)
            another = input("Add another player? (y/n): ")
            if another != 'y':
                break
    bj = BlackJack(players)
    while not bj.game_finished():
        print('\n\n' + bj.get_game_state_str(show_hole=False) + '\n\n')
        print(f"Current player: {bj.get_current_player_name()}")
        choice = input("Hit or Stand? (h/s): ")
        if choice == 'h':
            bj.hit_current_player()
        elif choice == 's':
            bj.stand_current_player()
        else:
            print("ERROR: wrong choice, input must be 'h' or 's'. Try again.")
            continue
    print('\n\n' + bj.get_game_state_str() + '\n\n')
    print('\n\n' + 'GAME HAS FINISHED:\n' + bj.get_game_result_str() + '\n\n')


if __name__ == '__main__':
    play_blackjack()