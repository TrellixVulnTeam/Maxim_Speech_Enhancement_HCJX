import torch
import torch.nn as nn

class SENetv0(nn.Module):

    # output = 161 STFT feats
    def __init__(self, num_channels=257, dimensions=(257, 1), bias=True, **kwargs):
        super().__init__() ## 继承nn.Module的属性

        self.project = nn.Sequential(

            nn.Conv1d(257, 256, 9), # in : 161 x 128; out: 256 x 120
            nn.ReLU(inplace=True),   
            
            nn.MaxPool1d(2),# in : 256 x 120; out: 256 x 60           
            nn.Conv1d(256, 128, 9),# in : 256 x 60; out: 128 x 52
            nn.ReLU(),
            nn.BatchNorm1d(128),
            
            #########################################################################
            nn.Conv1d(128, 128, 9, padding=4),# in : 128 x 52; out: 128 x 52
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Conv1d(128, 128, 9, padding=4),# in : 128 x 52; out: 128 x 52
            nn.ReLU(),
            nn.BatchNorm1d(128),
            #########################################################################
            nn.MaxPool1d(2),# in : 128 x 52; out: 128 x 26
            
            nn.Conv1d(128, 96, 9),# in : 128 x 26, out: 96 x 18
            nn.ReLU(),
            nn.BatchNorm1d(96),
            nn.MaxPool1d(2), # in : 96 x 18, out: 96 x 9            
            nn.Conv1d(96, 257, 9), # in : 96 x 9, out: 161 x 1
            nn.ReLU()
        )

    def forward(self, dt):
        x = dt['x']  # in: (batch, frequency, time), out:(batch, frequency, time)
        x = self.project(x) # in:(batch_size, 257, 128) out:(batch_size, 257, 1)
        dt['pred_y'] = torch.squeeze(x)
        return dt

class CNNBlock(nn.Module):

    def __init__(self, channel_in, channel_out, kernel_size=3, dilation=1, stride=1, padding=0):

        super(CNNBlock, self).__init__()

        self.f = nn.Sequential(
            nn.Conv1d(
                channel_in, 
                channel_out, 
                kernel_size=kernel_size,
                stride=stride, 
                padding=padding, 
                dilation=dilation),

            nn.BatchNorm1d(channel_out),

            nn.LeakyReLU(negative_slope=0.1)
        )

    def forward(self, x):

        return self.f(x)

class SENetv1(nn.Module):
    """
    1 torch.Size([100, 257, 128])  ->  torch.Size([100, 768, 128]) # 1x1 conv point-wise?
    2 torch.Size([100, 768, 128])  ->  torch.Size([100, 768, 64])
    3 torch.Size([100, 768, 64])  ->  torch.Size([100, 768, 32])
    4 torch.Size([100, 768, 32])  ->  torch.Size([100, 768, 16])
    5 torch.Size([100, 768, 16])  ->  torch.Size([100, 768, 8])
    6 torch.Size([100, 768, 8])  ->  torch.Size([100, 768, 4])
    7 torch.Size([100, 768, 4])  ->  torch.Size([100, 768, 2])
    8 torch.Size([100, 768, 2])  ->  torch.Size([100, 768, 1])
    9 torch.Size([100, 768, 1])  ->  torch.Size([100, 257, 1])
    """
    def __init__(self, freq_bin = 257, hidden_dim = 768, num_layer = 7, kernel_size = 3):
        super(SENetv1, self).__init__()

        input_layer = CNNBlock(freq_bin, hidden_dim, kernel_size=1)

        down_block = CNNBlock(hidden_dim, hidden_dim, kernel_size, padding=kernel_size//2)

        pooling_block = nn.MaxPool1d(kernel_size, stride=2, padding=kernel_size//2)

        output_layer = CNNBlock(hidden_dim, freq_bin, kernel_size, padding=kernel_size//2)

        self.encoder = nn.ModuleList()
        self.encoder.append(input_layer)
        for i in range(num_layer):
            self.encoder.append(nn.Sequential(
                down_block,
                pooling_block
            )
        )
        self.encoder.append(output_layer)    

    def forward(self, dt):
        x = dt['x']
        for layer in self.encoder:
            x = layer(x)
        dt['pred_y'] = torch.squeeze(x)
        return dt


    

    
    
    


class SENetv2(nn.Module):
    """
    1 torch.Size([100, 257, 128])  ->  torch.Size([100, 768, 128])
    2 torch.Size([100, 768, 128])  ->  torch.Size([100, 768, 64])
    3 torch.Size([100, 768, 64])  ->  torch.Size([100, 768, 32])
    4 torch.Size([100, 768, 32])  ->  torch.Size([100, 768, 16])
    5 torch.Size([100, 768, 16])  ->  torch.Size([100, 768, 8])
    6 torch.Size([100, 768, 8])  ->  torch.Size([100, 768, 4])
    7 torch.Size([100, 768, 4])  ->  torch.Size([100, 768, 2])
    8 torch.Size([100, 768, 2])  ->  torch.Size([100, 768, 1])
    9 torch.Size([100, 768, 1])  ->  torch.Size([100, 257, 1])
    """
    def __init__(self, freq_bin = 257, hidden_dim = 768, num_layer = 7, kernel_size = 3):
        super(SENetv2, self).__init__()

        input_layer = CNNBlock(freq_bin, hidden_dim, kernel_size, padding=kernel_size//2)

        down_block = CNNBlock(hidden_dim, hidden_dim, kernel_size, padding=kernel_size//2)

        pooling_block = nn.MaxPool1d(kernel_size, stride=2, padding=kernel_size//2)

        output_layer = CNNBlock(hidden_dim, freq_bin, kernel_size, padding=kernel_size//2)

        self.encoder = nn.ModuleList()
        self.encoder.append(input_layer)
        for i in range(num_layer):
            self.encoder.append(nn.Sequential(
                down_block,
                pooling_block
            )
        )
        self.encoder.append(output_layer)    

    def forward(self, dt):
        x = dt['x']
        for layer in self.encoder:
            x = layer(x)
        dt['pred_y'] = torch.squeeze(x)
        return dt
