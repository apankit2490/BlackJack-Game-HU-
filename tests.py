from unittest import TestCase

from blackjack import BlackJack, Deck, Card


def make_card(code):
    """
    Returns a Card object for a card code.
    Choices are: a, 2, 3, 4, 5, 6, 7, 8, 9, 10, k, q, j
    """
    CODE_TO_CARD = {
        'a': Card(Card.CardType.ACE, 1),
        '2': Card(Card.CardType.TWO, 2),
        '3': Card(Card.CardType.THREE, 3),
        '4': Card(Card.CardType.FOUR, 4),
        '5': Card(Card.CardType.FIVE, 5),
        '6': Card(Card.CardType.SIX, 6),
        '7': Card(Card.CardType.SEVEN, 7),
        '8': Card(Card.CardType.EIGHT, 8),
        '9': Card(Card.CardType.NINE, 9),
        '10': Card(Card.CardType.TEN, 10),
        'k': Card(Card.CardType.KING, 10),
        'q': Card(Card.CardType.QUEEN, 10),
        'j': Card(Card.CardType.JACK, 10),
    }
    code = code.lower()
    if code not in CODE_TO_CARD:
        raise ValueError(f"Code has to be one of {', '.join(CODE_TO_CARD.keys())}, got {code}")
    return CODE_TO_CARD[code]


def make_cards(codes):
    """
    Convenience method to convert a list of card codes to Card objects.
    """
    return [make_card(code) for code in codes]


class MockDeck(Deck):
    """
    Mocks a deck of cards. Allows to control the exact order in which cards are drawn.
    """

    def __init__(self, card_codes):
        """
        :param card_codes: A sequence of codes denoting cards that will be drawn from the deck.
                           Example: ['a', '2', '4', 'k', ...]
        """
        super().__init__()
        self.cards = make_cards(reversed(card_codes))


class BlackjackTestCase(TestCase):

    def _run_game(self, *, players, cards, moves):
        """
        Accepts a list of players, the order of cards drawn from a deck,
        the moves the players make, runs game and returns the BlackJack object
        """
        self.assertGreaterEqual(len(cards), (len(players) + 1) * 2,
                                msg=f"There must be atleast 2 cards each for each player and the "
                                    f"dealer, got {len(cards)} between {len(players)} players")
        bj = BlackJack(players, deck=MockDeck(cards))
        for move in moves:
            if move == 'h':
                bj.hit_current_player()
            elif move == 's':
                bj.stand_current_player()
        return bj

    def test_dealing_initial_cards(self):
        """
        Tests that the initial dealing happens correctly.
        """
        players = ['player1', 'player2', 'player3', 'player4']
        cards = ['a', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'k', 'q', 'j']
        bj = self._run_game(players=players, cards=cards, moves=[])
        game_state = bj.get_game_state()
        # Check each player got the right cards
        for i, player in enumerate(players):
            self.assertListEqual(game_state['players'][player]['hand'], make_cards(cards[i*2:i*2+2]))
        # Check that the dealer got the right cards
        self.assertEqual(game_state['dealer']['hand'], make_cards(cards[len(players) * 2: len(players) * 2 + 2]))

    def test_blackjack(self):
        players = ['nishant']
        cards = ['10', '10', '3', '4', 'a', '5', '6']
        moves = ['h', 's']
        bj = self._run_game(players=players, cards=cards, moves=moves)
        game_state = bj.get_game_state()
        self.assertTrue(game_state['finished'])
        game_results = bj.get_game_result()
        self.assertEqual(game_results[players[0]], 'WON')
