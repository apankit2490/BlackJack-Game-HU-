from unittest import TestCase, main
from pprint import pformat

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

GAME_TESTS = [
    {
        # p2 shoud bust, p1 (20) should lose against dealer (21)
        "players": ['p1', 'p2'],
        "cards": [
            'a', '2',
            '3', '4',
            '5', '6',
            '7', '8', '9', '10',
        ],
        "moves": {
            'p1': ['h', 's'],
            'p2': ['h', 'h'],
        },
        "results": {
            'p1': 'LOST',
            'p2': 'BUST',
        }
    },
    {
        # p2 should go bust, p1 (20) should win against dealer (bust)
        "players": ['p1', 'p2'],
        "cards": [
            'a', '2',
            '3', '4',
            '5', '10',
            '7', '8', '9', '10',
        ],
        "moves": {
            'p1': ['h', 's'],
            'p2': ['h', 'h'],
        },
        "results": {
            'p1': 'WON',
            'p2': 'BUST',
        }
    },
    {
        # p1 (4) and p2 (4) should lose against dealer (bust)
        "players": ['p1', 'p2'],
        "cards": [
            '2', '2',
            '2', '2',
            'a', 'k',
        ],
        "moves": {
            "p1": ['s'],
            "p2": ['s'],
        },
        "results": {
            "p1": "LOST",
            "p2": "LOST",
        }
    }
]


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
        for player, player_moves in moves.items():
            for move in player_moves:
                self.assertEqual(player, bj.get_current_player_name(), msg=f"It is not {player}'s turn. Game state:\n{pformat(bj.get_game_state())}")
                if move == 'h':
                    bj.hit_current_player()
                elif move == 's':
                    bj.stand_current_player()
                else:
                    raise ValueError(move)
        return bj

    def test_dealing_initial_cards(self):
        """
        Tests that the initial dealing happens correctly.
        """
        players = ['player1', 'player2', 'player3', 'player4']
        cards = ['a', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'k', 'q', 'j']
        bj = self._run_game(players=players, cards=cards, moves={})
        game_state = bj.get_game_state()
        # Check each player got the right cards
        for i, player in enumerate(players):
            self.assertListEqual(game_state['players'][player]['hand'], make_cards(cards[i*2:i*2+2]))
        # Check that the dealer got the right cards
        self.assertEqual(game_state['dealer']['hand'], make_cards(cards[len(players) * 2: len(players) * 2 + 2]))

    def _test_blackjack(self, players, cards, moves, results):
        bj = self._run_game(players=players, cards=cards, moves=moves)
        game_state = bj.get_game_state()
        self.assertTrue(game_state['finished'], msg=f'Game has not finished. Game state:\n{pformat(game_state)}')
        game_results = bj.get_game_result()
        for player, expected_result in results.items():
            actual_result = game_results[player]
            self.assertEqual(actual_result, expected_result, msg=pformat(bj.get_game_state()))

    def test_blackjack(self):
        for game in GAME_TESTS:
            players = game['players']
            cards = game['cards']
            moves = game['moves']
            results = game['results']
            try:
                self._test_blackjack(players, cards, moves, results)
            except Exception:
                print(f"FAILED:\n{pformat(game)}")
                raise


if __name__ == '__main__':
    main()
