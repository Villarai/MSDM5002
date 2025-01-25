import numpy as np

from array_operations import ext_radial, ext_angular, mask_extended
from array_operations import diagonal_view1, diagonal_view2
from array_operations import max_chessline_dim0

from Player import BasicPlayer,PassivePlayer,MonteCarloPlayer
from StrategyZY import MinMaxMonteCarloPlayer

# ai = BasicPlayer()
# ai = PassivePlayer()
ai = MinMaxMonteCarloPlayer()

def computer_move(board: np.ndarray, color: int):
    pred = ai.move(board, color)

    # print(ai)

    return pred

# Global check, high-consumption.
# Inside AI, instead, use quick_check(pos)
def check_winner(board: np.ndarray, display=False):
    return ai.check_winner(board, display)

def test_quick_check(idx, color):
    return ai.check_winner(board=None, quick=True, latest_move=idx, color=color)


