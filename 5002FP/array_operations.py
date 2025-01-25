import numpy as np
from numpy.lib.stride_tricks import as_strided

def diagonal_view1(board: np.ndarray):
    n_row, n_col = board.shape
    roll_indices=(np.arange(n_row)[:,None]+np.arange(n_col)[None,:])%n_row
    return board[roll_indices, np.arange(n_col)]

def diagonal_view2(board: np.ndarray):
    n_row, n_col = board.shape
    roll_indices=(np.arange(n_row)[:,None]-np.arange(n_col)[None,:])%n_row
    return board[roll_indices, np.arange(n_col)]

def ext_angular(board: np.ndarray, extension: int = 4):
    n_row, n_col = board.shape
    top = board[:extension,:]
    bot = board[n_row-extension:n_row,:]
    return np.concatenate([bot, board, top], axis=0)

def ext_radial(board: np.ndarray, extension: int = 4):
    n_row, n_col = board.shape
    outer_left = board[np.arange(n_row)-(n_row>>1), 1:1+extension]
    outer_left = np.flip(outer_left, axis=1)  # 反转列顺序
    return np.concatenate([outer_left, board, np.zeros_like(outer_left)], axis=1)

def mask_extended(board: np.ndarray, extension: int = 4):
    n_row, n_col = board.shape
    board[:extension,:extension] = 0
    board[n_row-extension:,:extension] = 0
    board[:,n_col-extension:] = 0
    return board

def depadding(board_ext: np.ndarray, padding: int = 4) -> np.ndarray:
    n_row, n_col = board_ext.shape
    board = board_ext[padding:n_row-padding, padding:n_col-padding]

    return board

def max_chessline_dim0(rowview: np.ndarray, color: int):
    rowview = np.equal(rowview,color).astype(int)

    # find value-changing points in a row
    padded=np.c_[np.zeros(rowview.shape[0], dtype=int), rowview, np.zeros(rowview.shape[0],dtype=int)]
    diff=np.diff(padded,axis=1)
    starts=np.where(diff==1)
    ends=np.where(diff==-1)
    lengths=ends[1]-starts[1]

    result = lengths.max() if lengths.size > 0 else 0

    return result

def kernel_nxn(kernel_size=3):
    assert kernel_size%2==1, f"kernel_size must be odd, got {kernel_size}"

    kernel=np.zeros((kernel_size, kernel_size), dtype=int)
    kernel[kernel_size>>1,:]=1
    kernel[:,kernel_size>>1]=1
    kernel[np.arange(kernel_size),np.arange(kernel_size)]=1
    kernel[np.arange(kernel_size),-np.arange(kernel_size)-1]=1

    return kernel

def zero_idxs(extended_arr: np.ndarray, padding=4):
    # Inverse extension, transform back to original board
    arr = depadding(extended_arr, padding=padding)
    condition = np.equal(arr, 0)
    zero_coords=np.argwhere(condition)

    return zero_coords



def sorted_available_zero_idxs(extended_arr: np.ndarray, kernel: np.ndarray, padding=4):
    kernel_size = 1+2*padding

    # n x n sliding window
    sliding_windows=np.lib.stride_tricks.sliding_window_view(extended_arr,(kernel_size, kernel_size))

    # Apply the kernel to the window. This can be a masking operation (e.g., "activation")
    neighborhood = sliding_windows*kernel
    # print(neighborhood.shape)

    # Count the non-zero elements in each 9x9 neighborhood (excluding the center)
    score_map=np.count_nonzero(neighborhood!=0,axis=(2,3))  # axis=(2,3) corresponds to the kernel dimensions
    # print(f"score_map\n{score_map}")

    # Inverse extension, transform back to original board
    arr = depadding(extended_arr, padding=padding)

    # Set the score map value to 0 for the positions where extended_arr is not zero
    score_map *= arr==0  # We only care about zero positions

    condition = np.equal(arr, 0)*np.greater(score_map, 0)

    # Get the coordinates of all the zero positions in extended_arr
    wanted_coords=np.argwhere(condition)

    # Extract the score values at the zero positions
    map_values=score_map[condition]

    # Combine the zero coordinates and their corresponding map values
    coords_with_values=list(zip(wanted_coords,map_values))

    # Sort the coordinates based on the map values (non-zero count in the neighborhood)
    sorted_coords=sorted(coords_with_values,key=lambda x: x[1],reverse=True)

    # Extract the sorted zero coordinates as a NumPy array
    sorted_zero_coords=np.array([coord[0] for coord in sorted_coords])

    return sorted_zero_coords, score_map



def kernel_slide(mat: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    # mat: (B, H+, W+)
    # kernel: (C, N, N)

    kernel_shape = kernel.shape
    # print(kernel_shape)

    # n x n sliding window
    unfolded=np.lib.stride_tricks.sliding_window_view(mat,(1, kernel_shape[1], kernel_shape[2]))
    # unfolded: (B, H, W, 1, N, N)
    # print(unfolded.shape)

    # Apply the kernel to the window. This can be a masking operation (e.g., "activation")
    unfolded = unfolded*kernel
    # unfolded: (B, H, W, C, N, N)
    # print(unfolded.shape)

    return unfolded

def convolve(mat: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    # mat: (B, H, W)
    # kernel: (C, N, N)

    conv = kernel_slide(mat, kernel)
    # conv: (B, H, W, C, N, N)

    conv = np.sum(conv, axis=(-2, -1))  # axis=(2,3) corresponds to the kernel dimensions
    # conv: (B, H, W, C)
    # print(conv.shape)

    return conv

def max_pooling(mat: np.ndarray) -> np.ndarray:
    # conv: (B, H, W, C)
    return np.max(mat, axis=-1)


def map2coords(map: np.ndarray):
    condition = np.greater(map, 0)
    zero_coords=np.argwhere(condition)

    return zero_coords
































