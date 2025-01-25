import numpy as np
import random
from tqdm import tqdm

from ChessBoard import ChessBoard

class BasicPlayer:
    def __init__(self, color=-1, margin=4, board_shape=(16, 10)):
        self.margin = margin
        self._chessboard_ = ChessBoard(shape=board_shape,margin=self.margin)
        self.__set_color__(color)
        self.__clear_imagination__()

    def __set_color__(self,color):
        self.color = color

    def __refresh_board__(self, board: np.ndarray):
        self._chessboard_.update_by(board)

    def __clear_imagination__(self):
        self.imaginary_steps = []

    def simulate_game(self, idx):
        if len(self.imaginary_steps)==0:
            imaginary_color = self.color
        else:
            imaginary_color = -1*self.imaginary_steps[-1][-1]

        self.imaginary_steps.append([idx[0], idx[1], imaginary_color])

        self._chessboard_.update_at(idx, imaginary_color)

        pass

    def rollback_simulation(self, n_step: int=-1):
        # Rolls back the last move in the simulation.
        # This ensures that the chessboard state is restored after each simulation step.

        if n_step==-1:
            n_step = len(self.imaginary_steps)

        while self.imaginary_steps:
            last_move=self.imaginary_steps.pop()  # Get the last move
            self._chessboard_.recall_at(last_move, self.color)  # Revert the move
            # print(last_move)
            n_step-=1
            if n_step==0:
                break

    def check_winner(self, board: np.ndarray, display=False, quick=False, **kwargs):
        if quick:
            return self._chessboard_.quick_check(**kwargs)

        self._chessboard_.update_by(board)
        if display:
            print(self._chessboard_)
        return self._chessboard_.global_check()

    def move(self, board: np.ndarray, color: int):
        self.__set_color__(color)
        self.__refresh_board__(board)
        self.__clear_imagination__()

        '''
        # edit from here, to implement moving strategies
        # i.e. random
        '''

        new_idx = self._chessboard_.random_idx()

        print(f"ai: {new_idx[0], new_idx[1]}")
        print(self._chessboard_)

        return new_idx




class PassivePlayer(BasicPlayer):
    def move(self, board: np.ndarray, color: int):
        self.__set_color__(color)
        self.__refresh_board__(board)
        self.__clear_imagination__()

        '''
        # edit from here, to implement moving strategies
        '''
        sorted_available_idx = self._chessboard_.coline5_available_idx()
        new_idx = sorted_available_idx[0]



        # output and return ai's move
        print(f"ai: {new_idx[0], new_idx[1]}")
        return new_idx




'''

现在我正在针对一个有一些特殊规则的五子棋游戏进行ai实现
这种特殊五子棋的规则已经被我完整实现在了一个叫作ChessBoard的类中，你无需知道具体的规则,我会向你介绍ChessBoard类可以调用的接口：
对于一个ChessBoard类的对象cb:

cb.global_check()返回一个int，值可能为0或1或-1或2，
其中，
0表示没有赢家，
1表示持有棋子颜色表示为“1”的玩家a获胜，
-1表示持有棋子颜色表示为“-1”的玩家b获胜，
2表示棋盘已满，且该情况也视为玩家b获胜

cb.all_available_idx()返回一个list，
list中每个元素均为tuple，形如(int, int)，表示在这个五子棋的一系列特殊规则下当前尚还可以进行落子的坐标

cb.preferred_available_idx()返回一个list，
list中每个元素均为tuple，形如(int, int)，表示在这个五子棋的一系列特殊规则下优先还可以进行落子的坐标
你可以用这个函数替代all_available_idx()以节约计算开支

cb.random_idx()返回一个tuple，是一个随机的位置，且该位置一定可以落子

cb.update_at(...)接收两个参数：idx和color
其中idx必须为一个tuple，即落子坐标
color必须为1或者-1，是落子的颜色
这个函数将会更新cb所记录的棋盘局面，将一个新的子落下

cb.recall_at(...)接收
其中idx必须为一个tuple，即想要撤回棋子的坐标
color必须为1或者-1，是要撤回的落子的颜色
这个函数将会更新cb所记录的棋盘局面，将一个已经存在的棋子撤回


现在我要写一个MonteCarloPlayer类，从基类BasicPlayer中继承了各种成员：
1.
self._chessboard_是ChessBoard类的实例，上面说的接口可以对此成员调用

2.
self.color: 该ai玩家持有的棋子颜色，只可能去1或-1

3.
self.imaginary_steps = [] 是一个初始为空的列表，被设计用于在ai模拟落子时保存它每一次落子的位置
从而方便回溯和前进
它应当被当作栈来使用

4. simulate_game()
进行一定次数的模拟，涉及对self.imaginary_steps的入栈操作
一般而言你是需要根据调用逻辑重写这个函数的

5. rollback_simulation(...)
回滚模拟中对——chessboard_的修改，涉及对imaginary_steps的出栈操作
可以接收一个int参数叫作n_steps,其用途为：
- 如果你的调用逻辑在回滚时并不总是回滚到初始状态，这个参数可以控制出栈次数，即实现局部回滚
- 默认n_steps为-1，这时会自动计算栈的当前大小并回滚全部进度
- 在基类中这个函数的实现为
    def rollback_simulation(self, n_step: int=-1):
        # Rolls back the last move in the simulation.
        # This ensures that the chessboard state is restored after each simulation step.

        if n_step==-1:
            n_step = len(self.imaginary_steps)

        while self.imaginary_steps:
            last_move=self.imaginary_steps.pop()  # Get the last move
            self._chessboard_.recall_at(last_move, self.color)  # Revert the move
            # print(last_move)
            n_step-=1
            if n_step==0:
                break
- 一般而言我认为基类的实现是够用的，如果你的实现中这个也够用，则不需要重写该方法


现在基于以上接口，帮我给MonteCarloPlayer类实现一个self.move()函数，针对self._chessboard_的当前局面进行蒙特卡洛搜索，可以在函数的输入中设置参数控制搜索深度等


你只需要实现这个类方法，不需要给出整个类的代码

'''



class MonteCarloPlayer(BasicPlayer):
    def __init__(self, color=-1, margin=4, board_shape=(16, 10), max_simulations=512, depth_limit=5):
        super().__init__(color, margin, board_shape)
        self.max_simulations = max_simulations
        self.depth_limit = depth_limit

    def move(self, board: np.ndarray, color: int):
        self.__set_color__(color)
        self.__refresh_board__(board)
        self.__clear_imagination__()

        """
        Executes the Monte Carlo Tree Search (MCTS) to determine the best move.

        :param max_simulations: Number of simulations to run for MCTS.
        :param depth_limit: Maximum depth for each simulation.
        :return: The best move as a tuple (row, col).
        """
        best_move=None
        best_win_count=-float('inf')

        if self._chessboard_.available_at((0, 0)):
            return (0, 0)


        # Get all available positions for this move
        # available_moves=self._chessboard_.coline5_available_idx()
        available_moves=self._chessboard_.prefered_available_idx()

        if len(available_moves)==1:
            best_move=available_moves[0]
        else:
            # Run simulations for each available move
            for move in tqdm(available_moves):
                # print(f"try start at {move}")

                win_count=0

                # Simulate the game from this move position
                for _ in range(self.max_simulations):
                    # Backup the current chessboard state
                    # original_state=self._chessboard_
                    # self._chessboard_=ChessBoard(self._chessboard_)  # Make a deep copy of the board

                    # Play the move
                    self._chessboard_.update_at(move,self.color)
                    self.imaginary_steps.append(move)  # Track this move

                    # Run the simulation (randomized play until the game ends)
                    winner=self.simulate_game()

                    # If the player wins in this simulation, increment the win count
                    # if winner==self.color:
                    #     win_count+=1
                    if winner==0:  # Draw
                        win_count+=1
                    elif winner==2:
                        if self.color==-1:
                            win_count+=10
                        else:
                            win_count-=10
                    elif winner==self.color:  # AI wins
                        win_count+=10
                    else: # Opponent wins, aka. winner==-self.color:
                        win_count-=10

                    # Rollback the move using imaginary_steps
                    self.rollback_simulation()

                # If the current move is better than the previous best move, update
                if win_count>best_win_count:
                    best_move=move
                    best_win_count=win_count

        print(f"ai: {best_move[0], best_move[1]}")
        return best_move

    def simulate_game(self):
        current_depth=0
        current_color=-self.color
        # current_color=self.color  # 1130 debug: 1st simu should use -self.color
        """
        Simulates a random game from the current state of the chessboard.

        
        :return: The winner of the simulated game (1 for player a, -1 for player b, 0 for draw).
        """

        while current_depth<self.depth_limit:
            # Get all available positions for the current player
            # available_moves=self._chessboard_.coline5_available_idx()
            available_moves=self._chessboard_.prefered_available_idx()
            if not available_moves:
                break  # No more moves available

            # Choose a random move
            move=random.choice(available_moves)
            # print(f"simu {move}")

            # Make the move
            self._chessboard_.update_at(move,current_color)
            self.imaginary_steps.append(move)  # Track this move

            # Check the game status
            game_status=self._chessboard_.quick_check(move, self.color)
            # game_status=self._chessboard_.global_check()
            if game_status!=0:  # If game over (win/loss/full)
                return game_status  # Return the winner (-1, 1) or 2 for a draw

            # Switch the turn to the other player
            current_color=-current_color
            current_depth+=1

        return 0  # Return 0 if it's a draw (game ends in full)


























