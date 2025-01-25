import numpy as np

from array_operations import convolve, max_pooling

class SlideKernel:
    def __init__(self, size: int=5, threshold: int=0):
        assert size%2==1, f"kernel_size must be odd, got {size}"

        self.size = size
        self.__init_kernel__()

        self.threshold = threshold

    def __init_kernel__(self):
        self._kernel_ = np.ones((self.size, self.size))

    def apply_on(self, arr: np.ndarray) -> np.array:
        assert len(arr.shape)==2, f"array muse be 2d, got arr.shape={arr.shape}"

        return np.greater(arr, self.threshold)


class ColineKernel(SlideKernel):
    def __init_kernel__(self):
        self._kernel_=np.zeros((1, self.size, self.size), dtype=int)
        self._kernel_[:, self.size>>1,:]=1
        self._kernel_[:, :,self.size>>1]=1
        self._kernel_[:, np.arange(self.size),np.arange(self.size)]=1
        self._kernel_[:, np.arange(self.size),-np.arange(self.size)-1]=1

    def apply_on(self,arr: np.ndarray) -> np.array:
        assert len(arr.shape)==2, f"array muse be 2d, got arr.shape={arr.shape}"

        ans=convolve(np.array([np.not_equal(arr, 0)*1]), self._kernel_)
        B, H, W, C = ans.shape # (B, H, W, C)
        ans = ans.reshape(H, W)

        return np.greater(ans, self.threshold)


# class SingleLineKernel(ScoringKernel):
#     def __init_kernel__(self):
#         self._kernel_=np.zeros((4, self.size, self.size), dtype=int)
#         self._kernel_[0, self.size>>1,:]=1
#         self._kernel_[1, :,self.size>>1]=1
#         self._kernel_[2, np.arange(self.size),np.arange(self.size)]=1
#         self._kernel_[3, np.arange(self.size),-np.arange(self.size)-1]=1
#         self._kernel_[:, self.size>>1, self.size>>1] = 0
#
#     def apply_on(self, arr: np.ndarray) -> np.array:
#         assert len(arr.shape)==2, f"array muse be 2d, got arr.shape={arr.shape}"
#
#         ans = convolve(np.array([(arr==1)*1, (arr==-1)*1]),self._kernel_)
#
#         B, H, W, C = ans.shape # (B, H, W, C)
#
#         ans = ans.reshape(B, -1, C).transpose(1, 0, 2).reshape(H, W, -1)
#         # ans = ans.swapaxes(0, 3).reshape(H, W, -1)
#         ans = max_pooling(ans)
#
#         return ans

class SingleLineKernel(SlideKernel):
    def __init__(self, size=9, threshold=0, weight=False):
        self.weight=weight
        super().__init__(size,threshold)

    def __init_kernel__(self):
        self._kernel_=np.zeros((4,self.size,self.size),dtype=int)
        self._kernel_[0,self.size>>1,:]=1
        self._kernel_[1,:,self.size>>1]=1
        self._kernel_[2,np.arange(self.size),np.arange(self.size)]=1
        self._kernel_[3,np.arange(self.size),-np.arange(self.size)-1]=1
        self._kernel_[:,self.size>>1,self.size>>1]=0
        if self.weight:
            axis=np.arange(9)
            axis=axis-4
            axis=5-np.abs(axis)
            axis=2*axis-1

            hori,vert=np.meshgrid(axis,axis)

            self._kernel_[0,:,:]*=hori
            self._kernel_[1,:,:]*=vert
            self._kernel_[2,:,:]*=hori
            self._kernel_[3,:,:]*=hori

    def apply_on(self,arr: np.ndarray) -> np.array:
        assert len(arr.shape)==2,f"array muse be 2d, got arr.shape={arr.shape}"

        ans=convolve(np.array([(1+arr)>>1, (1-arr)>>1]),self._kernel_)
        # ans=convolve(np.array([(arr==1)*1,(arr==-1)*1]),self._kernel_)
        B,H,W,C=ans.shape  # (B, H, W, C)

        ans=ans.reshape(B,-1,C).transpose(1,0,2).reshape(H,W,-1)
        # ans = ans.swapaxes(0, 3).reshape(H, W, -1)
        ans=max_pooling(ans)

        return ans

class EvilConvolutionalVictoryDetector(SlideKernel):
    def __init_kernel__(self):
        self._kernel_=np.zeros((4,self.size,self.size),dtype=int)

        mid = self.size>>1

        self._kernel_[0, mid, 0:mid+1]=1
        self._kernel_[1, mid>>1: (mid>>1)+mid+1, mid+1]=1
        self._kernel_[2, np.arange(mid, self.size), np.arange(mid, self.size)]=1
        self._kernel_[3, -np.arange(mid, self.size)-1, np.arange(mid, self.size)]=1

        print(self._kernel_)

    def apply_on(self,arr: np.ndarray) -> np.array:
        assert len(arr.shape)==2,f"array muse be 2d, got arr.shape={arr.shape}"

        victories=convolve(np.array([arr]), self._kernel_)
        victories=np.abs(victories)
        # victories=convolve(np.array([(1+arr)>>1, (1-arr)>>1]), self._kernel_)
        B,H,W,C=victories.shape  # (B, H, W, C)

        victories = victories.reshape(B, -1)  # (B,H*W*c)
        victories = np.max(victories, axis=-1)>4

        return victories*1















































