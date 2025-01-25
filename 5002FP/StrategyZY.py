import numpy as np
import random
from tqdm import tqdm
from ChessBoard import ChessBoard
from Player import BasicPlayer


class MinMaxMonteCarloPlayer(BasicPlayer):
    def __init__(self, color=-1, margin=4, board_shape=(16, 10), max_depth=5, simulations=100):
        self.margin = margin
        self._chessboard_ = ChessBoard(shape=board_shape, margin=self.margin)
        self.__set_color__(color)
        self.max_depth = max_depth
        self.simulations = simulations

    def __set_color__(self, color):
        self.color = color

    def __refresh_board__(self, board: np.ndarray):
        self._chessboard_.update_by(board)

    def possible_moves(self, board):
        return [(i, j) for i in range(board.shape[0]) for j in range(board.shape[1]) if board[i, j] == 0]

    def minmax(self, board, depth, maximizing_player):
        winner = check_winner(board)
        if winner != 0 or depth == 0:
            return winner  # Return the score

        if maximizing_player:
            max_eval = -np.inf
            for move in self.possible_moves(board):
                new_board = board.copy()
                new_board[move] = self.color
                eval = self.minmax(new_board, depth - 1, False)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = np.inf
            for move in self.possible_moves(board):
                new_board = board.copy()
                new_board[move] = -self.color
                eval = self.minmax(new_board, depth - 1, True)
                min_eval = min(min_eval, eval)
            return min_eval

    def monte_carlo_simulation(self, board):
        current_board = board.copy()
        current_color = -self.color

        while True:
            moves = self.possible_moves(current_board)
            if not moves:
                break
            move = random.choice(moves)
            current_board[move] = current_color
            current_color = -current_color

            if self.check_winner(current_board) != 0:
                return current_color  # Return the winner

        return 0  # Draw

    def move(self, board: np.ndarray, color: int):
        best_move = None
        best_value = -np.inf

        for move in self.possible_moves(board):
            total_wins = 0
            for _ in range(self.simulations):
                new_board = board.copy()
                new_board[move] = color
                result = self.monte_carlo_simulation(new_board)
                if result == color:
                    total_wins += 1
            
            value = total_wins / self.simulations  # Win ratio
            if value > best_value:
                best_value = value
                best_move = move

        return best_move