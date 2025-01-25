import numpy as np
from numpy.lib.stride_tricks import as_strided

from colorama import Fore,Back

from array_operations import ext_radial, ext_angular, mask_extended, depadding
from array_operations import diagonal_view1, diagonal_view2
from array_operations import map2coords, zero_idxs, sorted_available_zero_idxs
from array_operations import max_chessline_dim0
from array_operations import kernel_nxn

from Kernel import ColineKernel, SingleLineKernel
from Kernel import EvilConvolutionalVictoryDetector

import random
import time
import matplotlib.pyplot as plt
from tqdm import trange


class ChessBoard:
    def __init__(self, shape: tuple, margin: int = 4):
        assert shape[0] % 2 == 0, f"n_ang(angular_span, shape[0]) must be an even integer, (got {shape[0]})"
        assert margin >= 0, f"margin must be a non-negative integer, (got {margin})"
        self.margin = margin
        self.n_ang, self.n_rad = shape[0], shape[1]
        self.n_row, self.n_col = self.n_ang+2*self.margin, self.n_rad+2*self.margin
        # self.ext_center = (self.n_row >> 1, self.margin)

        self.__init_board__()
        self.__init_kernel__()

    def __init_board__(self):
        self._board_ = np.zeros(shape=(self.n_ang,self.n_rad),dtype=int)

    def __init_kernel__(self):
        # self.scoring_kernel = kernel_nxn(5)
        # print(self.scoring_kernel)
        self.scoring_kernel = SingleLineKernel(weight=True)
        # self.scoring_kernel = ColineKernel()

        self.evil_kernel = EvilConvolutionalVictoryDetector(size=9)

    def update_by(self, board: np.ndarray):
        self._board_ = np.copy(board)

    def update_at(self, idx: tuple, color):
        assert self.available_at(idx), f"idx={idx} is occupied. please debug."
        assert color in [-1, 1], f"illegal color: {color}"

        if idx[1]==0:
            self._board_[:,0] = color
        else:
            self._board_[idx] = color

    def recall_at(self, idx: tuple, color):
        assert not self.available_at(idx), f"idx={idx} is empty. please debug."
        assert color in [-1, 1], f"illegal color: {color}"
        # assert self._board_[idx]==color,f"wrong recall, color diff. please debug"

        if idx[1]==0:
            self._board_[:,0] = 0
        else:
            self._board_[idx] = 0

    def extended(self):
        ext_board = ext_radial(np.copy(self._board_),self.margin)
        ext_board = ext_angular(ext_board, self.margin)
        ext_board = mask_extended(ext_board, self.margin)
        return ext_board

    def available_at(self, idx):
        return self._board_[idx]==0

    def global_check(self):
        chessline_detect = []
        ext_board = self.extended()

        # check horizontal lines
        chessline_detect.append([
            max_chessline_dim0(ext_board,color=1),
            max_chessline_dim0(ext_board,color=-1),
        ])
        # check vertical lines
        chessline_detect.append([
            max_chessline_dim0(np.transpose(ext_board[:, self.margin+1:]),color=1),
            max_chessline_dim0(np.transpose(ext_board[:, self.margin+1:]),color=-1),
        ])

        # check main-diagonal lines
        main_diag = diagonal_view1(ext_board[self.margin:self.margin+self.n_ang, self.margin:])
        # main_diag = diagonal_view1(ext_board[:, self.margin:])  # 1201 bug found
        chessline_detect.append([
            max_chessline_dim0(main_diag,color=1),
            max_chessline_dim0(main_diag,color=-1),
        ])

        # check sub-diagonal lines
        sub_diag = diagonal_view2(ext_board[self.margin:self.margin+self.n_ang, self.margin:])
        # sub_diag = diagonal_view2(ext_board[:, self.margin:])  # 1201 bug found
        chessline_detect.append([
            max_chessline_dim0(sub_diag,color=1),
            max_chessline_dim0(sub_diag,color=-1),
        ])

        victories = np.max(chessline_detect, axis=0)>4
        result=1*victories

        result=2*np.prod(result)+np.sum(result*np.array([1,-1]))

        # win     result
        # 0, 0    0 if board is not full, else 2
        # 1, 0    1
        # 0, 1    -1
        # 1, 1    2

        if np.all(self._board_) and result==0:
            return 2
        return result

    def evil_global_check(self):
        evil_result = self.evil_kernel.apply_on(self.extended())

        evil_result=2*np.prod(evil_result)+np.sum(evil_result*np.array([1,-1]))

        # win     evil_result
        # 0, 0    0 if board is not full, else 2
        # 1, 0    1
        # 0, 1    -1
        # 1, 1    2

        if np.all(self._board_) and evil_result==0:
            return 2
        return evil_result

    def quick_check(self, latest_move, color):
        # latest_move: (int, int)
        if latest_move[1]==0:
            # return self.global_check()
            return self.evil_global_check()

        chip_size = 2*self.margin+1
        center = self.margin

        ang, rad = latest_move
        ang = (ang+self.n_ang)%self.n_ang

        chip = np.equal(self.extended()[ang:ang+chip_size, rad:rad+chip_size], color)
        # chip = self.extended()[ang:ang+chip_size, rad:rad+chip_size]
        # print(chip.shape)
        # print(f"quick check\nmove:\n{latest_move}\nchip:\n{chip*1}")

        chessline_sum = np.array([
            1,             # 0: hori [backward, forward]
            1,             # 1: verti [backward, forward]
            1,             # 2: maindiag [backward, forward]
            1,             # 3: subdiag [backward, forward]
        ])
        update_sum = np.array([
            [1, 1],             # 0: hori [backward, forward]
            [1, 1],             # 1: verti [backward, forward]
            [1, 1],             # 2: maindiag [backward, forward]
            [1, 1],             # 3: subdiag [backward, forward]
        ])

        for i in range(1, self.margin+1):
            lo, hi = center-i, center+i

            # print(f"lo, hi = {lo, hi}")

            # horizontal backward
            if update_sum[0, 0]:
                if chip[center, lo]:
                    # print(f"hori back ({center, lo})")
                    chessline_sum[0] += 1
                else:
                    update_sum[0, 0] = 0
            # horizontal forward
            if update_sum[0, 1]:
                if chip[center, hi]:
                    # print(f"hori fore ({center, hi})")
                    chessline_sum[0] += 1
                else:
                    update_sum[0, 1] = 0

            # vertical backward
            if update_sum[1, 0]:
                if chip[lo, center]:
                    # print(f"vert back ({lo, center})")
                    chessline_sum[1] += 1
                else:
                    update_sum[1, 0] = 0
            # vertical forward
            if update_sum[1, 1]:
                if chip[hi, center]:
                    # print(f"vert fore ({hi, center})")
                    chessline_sum[1] += 1
                else:
                    update_sum[1, 1] = 0

            # diagonal backward
            if update_sum[2, 0]:
                if rad-i<0:
                    update_sum[2, 0] = 0
                elif chip[lo, lo]:
                    # print(f"diag back ({lo, lo})")
                    chessline_sum[2] += 1
                else:
                    update_sum[2, 0] = 0
            # diagonal forward
            if update_sum[2, 1]:
                if chip[hi, hi]:
                    # print(f"diag fore ({hi, hi})")
                    chessline_sum[2] += 1
                else:
                    update_sum[2, 1] = 0

            # subdiagonal backward
            if update_sum[3, 0]:
                if rad-i<0:
                    update_sum[3, 0] = 0
                elif chip[hi, lo]:
                    # print(f"anti back ({hi, lo})")
                    chessline_sum[3] += 1
                else:
                    update_sum[3, 0] = 0
            # subdiagonal forward
            if update_sum[3, 1]:
                if chip[lo, hi]:
                    # print(f"anti fore ({lo, hi})")
                    chessline_sum[3] += 1
                else:
                    update_sum[3, 1] = 0

        # raise RuntimeError('pause')

        win = np.max(chessline_sum)>4

        if win:
            return color
        elif color==-1 and np.all(self._board_):
            return 2
        else:
            return 0



    # provide a random available position on the board
    def random_idx(self):
        regenerate = True
        while regenerate:
            # angular, (row), [-n_ang/2, n_ang/2)
            ang = np.random.randint(low=-(self.n_ang>>1), high=(self.n_ang>>1))
            # radial, (col), [-n_rad/2, n_rad/2)
            rad = np.random.randint(low=0, high=self.n_rad)

            idx = (ang, rad)

            regenerate = not self.available_at(idx)

        return idx

    def all_available_idx(self):
        zero_coords = zero_idxs(self.extended(), padding=self.margin)

        # these three lines's purpose:
        # transfer the dim-0 values from [0, n) to [-n/2, n/2)
        # then it can be used in main()
        zero_coords[:, 0] += self.n_ang>>1
        zero_coords[:, 0] %= self.n_ang
        zero_coords[:, 0] -= self.n_ang>>1

        idx_list = [(coord[0],coord[1]) for coord in list(zero_coords)]

        return idx_list


    def coline5_available_idx(self):
        padding = 2
        depad = self.margin-padding

        sorted_zero_coords, score_map = sorted_available_zero_idxs(depadding(self.extended(), padding=depad),self.scoring_kernel,padding=padding)

        # these three lines's purpose:
        # transfer the dim-0 values from [0, n) to [-n/2, n/2)
        # then it can be used in main()
        sorted_zero_coords[:, 0] += self.n_ang>>1
        sorted_zero_coords[:, 0] %= self.n_ang
        sorted_zero_coords[:, 0] -= self.n_ang>>1

        idx_list = [(coord[0],coord[1]) for coord in list(sorted_zero_coords)]

        return idx_list

    def prefered_available_idx(self):
        padding = 4
        depad = self.margin-padding

        ext_board = self.extended()
        if depad>0:
            ext_board = depadding(ext_board, padding=depad)
        score_map = self.scoring_kernel.apply_on(ext_board)
        score_map = score_map*np.equal(self._board_, 0)*1

        coords = map2coords(np.equal(score_map, np.max(score_map)))
        coords[:, 0] += self.n_ang>>1
        coords[:, 0] %= self.n_ang
        coords[:, 0] -= self.n_ang>>1
        # these three lines's purpose:
        # transfer the dim-0 values from [0, n) to [-n/2, n/2)
        # then it can be used in main()

        idx_list = [(coord[0],coord[1]) for coord in list(coords)]

        return idx_list


    def __repr__(self):
        text=f"ExtendedChessBoard{' '*27}Diagonal{' '*39}AntiDiagonal\n"

        ext_board = self.extended()
        main_diag = diagonal_view1(self._board_)
        sub_diag = diagonal_view2(self._board_)


        # available_moves = self.coline5_available_idx()
        available_moves = self.prefered_available_idx()
        print(f"# available moves = {len(available_moves)}")

        for row in range(self.n_row):
            for col in range(self.n_col):
                status=ext_board[row, col]
                if status==-1:
                    marker='X'
                elif status==1:
                    marker='O'
                elif 0<=(row-self.margin)<self.n_ang and 0<=(col-self.margin)<self.n_rad:
                    check_idx = ((row-self.margin+(self.n_ang>>1))%self.n_ang-(self.n_ang>>1), col-self.margin)
                    if check_idx in available_moves:
                        marker = f"{Fore.GREEN}*{Fore.RESET}"
                    else:
                        marker = '·'
                else:
                    marker='·'
                text+=f"{marker} "
                if col in [3,4,8,3+self.n_rad]:
                    text+='| '
            text+=' # '
            for col in range(self.n_col):
                ang, rad = row-self.margin, col-self.margin
                if 0<=ang<self.n_ang and 0<=rad<self.n_rad:
                    status=main_diag[ang, rad]
                    if status==-1:
                        marker='X'
                    elif status==1:
                        marker='O'
                    else:
                        marker='·'
                else:
                    marker=' '
                text+=f"{marker} "
                if col in [3,4,8,3+self.n_rad]:
                    text+='| '
            text+=' # '
            for col in range(self.n_col):
                ang, rad = row-self.margin, col-self.margin
                if 0<=ang<self.n_ang and 0<=rad<self.n_rad:
                    status=sub_diag[ang, rad]
                    if status==-1:
                        marker='X'
                    elif status==1:
                        marker='O'
                    else:
                        marker='·'
                else:
                    marker=' '
                text+=f"{marker} "
                if col in [3,4,8,3+self.n_rad]:
                    text+='| '
            text+='\n'
            if row in [3,3+(self.n_ang>>1),3+self.n_ang]:
                text+='-'*(8+4+self.n_rad)*2
                text+=' # '
                text+='-'*(8+4+self.n_rad)*2
                text+=' # '
                text+='-'*(8+4+self.n_rad)*2
                text+='\n'

        return text



    def benchmark_check(self, simu = 1000):
        board_backup = np.copy(self._board_)

        available_moves=self.all_available_idx()

        global_rec = []
        evil_rec = []
        quick_rec = []

        for _t in trange(simu):
            random.shuffle(available_moves)

            end_mem=[]

            self.update_by(board_backup)
            color = 1
            count = 0
            t_rec = time.time()
            center_occupied = False
            for move in available_moves:
                if not center_occupied:
                    if move[1]==0:
                        center_occupied=True
                    self.update_at(move, color)
                    winner = self.global_check()
                    count+=1
                    color = -color
                    if winner!=0:
                        break
            t_rec = time.time()-t_rec
            global_rec.append([count, t_rec])

            end_mem.append(np.copy(self._board_))

            self.update_by(board_backup)
            color = 1
            count = 0
            t_rec = time.time()
            center_occupied = False
            for move in available_moves:
                if not center_occupied:
                    if move[1]==0:
                        center_occupied=True
                    self.update_at(move, color)
                    winner = self.evil_global_check()
                    count+=1
                    color = -color
                    if winner!=0:
                        break
            t_rec = time.time()-t_rec
            evil_rec.append([count, t_rec])

            end_mem.append(np.copy(self._board_))

            self.update_by(board_backup)
            color = 1
            count = 0
            t_rec = time.time()
            center_occupied = False
            for move in available_moves:
                if not center_occupied:
                    if move[1]==0:
                        center_occupied=True
                    self.update_at(move, color)
                    winner = self.quick_check(move, color)
                    count+=1
                    color = -color
                    if winner!=0:
                        break
            t_rec = time.time()-t_rec
            quick_rec.append([count, t_rec])

            end_mem.append(np.copy(self._board_))

            counts = [global_rec[-1][0], evil_rec[-1][0], quick_rec[-1][0]]
            if counts[0]==counts[1] and counts[0]==counts[2]:
                pass
            else:
                for i in range(len(available_moves)):
                    print(f"{i}:\t{available_moves[i]}")
                for mem in end_mem:
                    print(mem)
                raise RuntimeError(f'Please debug, different results:\n{counts}')

        global_rec = np.array(global_rec)
        evil_rec = np.array(evil_rec)
        quick_rec = np.array(quick_rec)

        plt.figure(figsize=(20,17), dpi=256)

        plt.scatter(global_rec[:,0], global_rec[:,1], label='global_check', marker='+')
        plt.scatter(evil_rec[:,0], evil_rec[:,1], label='evil_global_check', marker='x')
        plt.scatter(quick_rec[:,0], quick_rec[:,1], label='quick_check', marker='o')

        plt.legend()

        plt.show()























