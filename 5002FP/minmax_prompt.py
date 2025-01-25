class MinMaxPlayer(BasicPlayer):
    def __init__(self,
                 chessboard: ChessBoard2d,
                 color=-1,
                 minmax_depth=3):
        # 调用父类构造函数
        super().__init__(chessboard, color)
        self.minmax_depth = minmax_depth  # MinMax搜索深度

    def move(self, board: np.ndarray, color: int):
        self.__set_color__(color)
        self.__refresh_board__(board)
        self.__clear_imagination__()

        # 获取所有可用的棋盘位置
        available_moves = self._chessboard_.prefered_available_idx()

        if len(available_moves) == 1:
            return available_moves[0]  # 如果只有一个可用位置，直接返回

        # 使用MinMax进行搜索
        best_move, best_score = self.minmax_search(self._chessboard_, 0, self.color, -float('inf'), float('inf'))

        return best_move

    def minmax_search(self, board: ChessBoard2d, depth: int, color: int, alpha: float, beta: float):
        # 如果达到了最大深度，进行启发式评分
        if depth == self.minmax_depth:
            score = self.evaluate_board(board, color)
            return None, score

        available_moves = board.prefered_available_idx()
        best_move = None

        if color == self.color:  # 最大化玩家
            max_score = -float('inf')
            for move in available_moves:
                board_copy = board.manta()  #复制当前局面信息
                board_copy.update_at(move, color)  #假设当前在move位置落子。更新局面信息
                _, score = self.minmax_search(board_copy, depth + 1, -color, alpha, beta)
                if score > max_score:
                    max_score = score
                    best_move = move
                alpha = max(alpha, score)
                if beta <= alpha:
                    break  # 剪枝
            return best_move, max_score
        else:  # 最小化玩家
            min_score = float('inf')
            for move in available_moves:
                board_copy = board.manta()
                board_copy.update_at(move, color)
                _, score = self.minmax_search(board_copy, depth + 1, -color, alpha, beta)
                if score < min_score:
                    min_score = score
                    best_move = move
                beta = min(beta, score)
                if beta <= alpha:
                    break  # 剪枝
            return best_move, min_score

    def evaluate_board(self, board: ChessBoard2d, color: int):

        # using monte carlo


        # 启发式评分：根据当前棋盘状态来评估局面
        score = 0

        # 启发式评分示例：优先可用位置评分
        available_moves = board.prefered_available_idx()
        for move in available_moves:
            # 假设优先位置得分较高，具体实现可以根据需求进一步调整
            score += 1  # 简单加分

        return score
















# import copy
#
# import numpy as np
# import random
# from tqdm import tqdm
# from multiprocessing import Pool
#
# from mypackage.chessboard import ChessBoard2d
#
# class BasicPlayer:
#     def __init__(self,chessboard: ChessBoard2d,color=-1):
#         self._chessboard_ = chessboard
#         self.__set_color__(color)
#         self.__clear_imagination__()
#
#     def __set_color__(self,color):
#         self.color = color
#
#     def __refresh_board__(self, board: np.ndarray):
#         self._chessboard_.update_by(board)
#
#     def __clear_imagination__(self):
#         self.imaginary_steps = []
#
#     def simulate_game(self, idx):
#         if len(self.imaginary_steps)==0:
#             imaginary_color = self.color
#         else:
#             imaginary_color = -1*self.imaginary_steps[-1][-1]
#
#         self.imaginary_steps.append([idx[0], idx[1], imaginary_color])
#
#         self._chessboard_.update_at(idx, imaginary_color)
#
#         pass
#
#     def rollback_simulation(self, n_step: int=-1):
#         # Rolls back the last move in the simulation.
#         # This ensures that the chessboard state is restored after each simulation step.
#
#         if n_step==-1:
#             n_step = len(self.imaginary_steps)
#
#         while self.imaginary_steps:
#             last_move=self.imaginary_steps.pop()  # Get the last move
#             self._chessboard_.recall_at(last_move, self.color)  # Revert the move
#             # print(last_move)
#             n_step-=1
#             if n_step==0:
#                 break
#
#     def check_winner(self, board: np.ndarray, quick=False, **kwargs):
#         if quick:
#             return self._chessboard_.quick_check(**kwargs)
#
#         self._chessboard_.update_by(board)
#         return self._chessboard_.global_check()
#
#
# class MultiprocessMonteCarloPlayer(BasicPlayer):
#     def __init__(self,
#                  chessboard: ChessBoard2d,
#                  color=-1,
#                  max_simulations=512,
#                  depth_limit=5,
#                  process_number=8):
#         super().__init__(chessboard,color)
#         self.max_simulations=max_simulations
#         self.depth_limit=depth_limit
#         self.mp_n = process_number
#
#     def move(self, board: np.ndarray, color: int):
#         self.__set_color__(color)
#         self.__refresh_board__(board)
#         self.__clear_imagination__()
#
#         """
#         Executes the Monte Carlo Tree Search (MCTS) to determine the best move.
#
#         :param max_simulations: Number of simulations to run for MCTS.
#         :param depth_limit: Maximum depth for each simulation.
#         :return: The best move as a tuple (row, col).
#         """
#
#         best_move=None
#         best_win_count=-float('inf')
#         available_moves=self._chessboard_.prefered_available_idx()
#
#         if len(available_moves)==1:
#             best_move=available_moves[0]
#         else:
#             if len(available_moves)<self.mp_n:
#                 n_process = len(available_moves)
#             else:
#                 n_process=self.mp_n
#
#             task_list = []
#             for move in available_moves:
#                 task_list.append(
#                     [self._chessboard_.manta(),
#                      move,
#                      self.color]
#                 )
#
#             pool = Pool(processes=n_process)
#             results=pool.map(self.simulate_game,task_list)
#             print(f"MCTScore:\n{results}")
#
#             for move, win_count in results:
#                 if win_count>best_win_count:
#                     best_move=move
#                     best_win_count=win_count
#
#         return best_move
#
#     def simulate_game(self, args):
#         cb, move, color = args
#
#         win_count = 0
#         for _ in range(self.max_simulations):
#             temp_cb=cb.manta()
#
#             current_depth=0
#             current_color=color
#             current_move=move
#
#             game_status=0
#
#             while current_depth<self.depth_limit:
#                 temp_cb.update_at(current_move,current_color)
#                 game_status=temp_cb.quick_check(current_move,self.color)
#                 if game_status!=0:  # If game over (win/loss/full)
#                     break  # found winner (-1, 1) or 2 for a draw
#                 current_color=-current_color
#                 current_depth+=1
#
#                 next_moves=temp_cb.prefered_available_idx()
#                 current_move=random.choice(next_moves)
#
#             if game_status==0:  # Draw
#                 win_count+=1
#             elif game_status==2:
#                 if color==-1:
#                     win_count+=10
#                 else:
#                     win_count-=10
#             elif game_status==color:  # self wins
#                 win_count+=10
#             else:  # Opponent wins
#                 win_count-=10
#
#         return move, win_count