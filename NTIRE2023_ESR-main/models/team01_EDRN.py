import torch
import torch.nn as nn
import torch.nn.functional as F
lrelu_value = 0.1
act = nn.LeakyReLU(lrelu_value)
def make_model(parent=False):
    return EDRN()
lrelu_value = 0.1
act = nn.LeakyReLU(lrelu_value)


class RepConv(nn.Module):
    def __init__(self, n_feats):
        super(RepConv, self).__init__()
        self.downconv = nn.Conv2d(n_feats,n_feats*2,3,1,1)
        self.rep_conv = nn.Conv2d(n_feats*2, n_feats*2, 3, 1, 1)
        self.upconv = nn.Conv2d(n_feats*2,n_feats,3,1,1)

    def forward(self, x):
        out = self.downconv(x)
        out - self.rep_conv(out)
        out = self.upconv(out)
        return out + x


class BasicBlock(nn.Module):
    """ Depth-wise separable Extraction Block for building DAB

    Args:
        n_feats (int): The number of feature maps.

    Diagram:
        --RepConv--LeakyReLU--RepConv--
        
    """


    def __init__(self, n_feats):
        super(BasicBlock, self).__init__()
        self.conv1 = RepConv(n_feats)
        self.conv2 = RepConv(n_feats)

    def forward(self, x):
        res = self.conv1(x)
        res = act(res)
        res = self.conv2(res)

        return res + x


class HFAB(nn.Module):
    """ Depth-wise separable Attention Block(DAB)

    args:
        n_feats (int): The number of input feature maps.
        up_blocks (int): The number of RepConv in this DAB.
        mid_feats (int): Input feature map numbers of RepConv.

    Diagram:
        --Reduce_dimension--[RepConv]*up_blocks--Expand_dimension--Sigmoid--

    """

    def __init__(self, n_feats, up_blocks, mid_feats):
        super(HFAB, self).__init__()
        self.squeeze = nn.Conv2d(n_feats, mid_feats, 3, 1, 1)
        convs = [BasicBlock(mid_feats) for _ in range(up_blocks)]
        self.convs = nn.Sequential(*convs)
        self.excitate = nn.Conv2d(mid_feats, n_feats, 3, 1, 1)
    
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out = act(self.squeeze(x))
        out = act(self.convs(out))
        out = self.excitate(out)
        out = self.sigmoid(out)
        out = out * x

        return out


class EDRN(nn.Module):
    """ 
    Efficient Deep Residual Network
    Diagram:
        --Conv--Conv-DAB-[DEB-DAB]*down_blocks-Conv-+-Upsample--
               |_____________________________________________|

    """

    def __init__(self):
        super(EDRN, self).__init__()

        self.down_blocks = 5

        up_blocks = [2, 1, 1, 1, 1,2]
        mid_feats = 16
        n_feats = 64
        n_colors = 3
        scale = 4

        # define head module
        self.head = nn.Conv2d(n_colors, n_feats, 3, 1, 1)

        # warm up
        self.warmup = nn.Sequential(
            nn.Conv2d(n_feats, n_feats, 3, 1, 1),
            HFAB(n_feats, up_blocks[0], mid_feats-4)
        )

        # define body module
        basic_blocks = [BasicBlock(n_feats) for _ in range(self.down_blocks)]
        hfabs = [HFAB(n_feats, up_blocks[i+1], mid_feats) for i in range(self.down_blocks)]

        self.basic_blocks = nn.ModuleList(basic_blocks)
        self.hfabs = nn.ModuleList(hfabs)

        self.lr_conv = nn.Conv2d(n_feats, n_feats, 3, 1, 1)

        # define tail module
        self.tail = nn.Sequential(
            nn.Conv2d(n_feats, n_colors*(scale**2), 3, 1, 1),
            nn.PixelShuffle(scale)
        )


    def forward(self, x):
        x = self.head(x)

        h = self.warmup(x)
        for i in range(self.down_blocks):
            h = self.basic_blocks[i](h)
            h = self.hfabs[i](h)
        h = self.lr_conv(h)

        h =h + x
        x = self.tail(h)

        return x