import torch
import torchvision.transforms as T

class Config:
    # network settings
    backbone = 'fmobile' # [resnet, fmobile]
    metric = 'arcface'  # [cosface, arcface]
    embedding_size = 512
    drop_ratio = 0.5

    # data preprocess
    input_shape = [3, 128, 128]
    train_transform = T.Compose([
        T.RandomHorizontalFlip(),  # 随机水平翻转（好像也没必要？）
        T.Resize(input_shape[1:]), # [1:]即表示忽略掉最前面channel的大小
        T.ToTensor(),
        T.Normalize(mean=[0.5], std=[0.5]),
    ])
    test_transform = T.Compose([
        T.Resize(input_shape[1:]), # [1:]即表示忽略掉最前面channel的大小
        T.ToTensor(),
        T.Normalize(mean=[0.5], std=[0.5]),
    ])

    # dataset
    train_root = 'pixiv_data/starrail_4avatarXall_train'
    test_root = 'pixiv_data/starrail_4avatarX10_test'
    test_list = 'pixiv_data/starrail_4avatarX10_test/test_pairs.txt'
    
    # training settings
    checkpoints = "checkpoints"
    restore = False
    restore_model = ""
    test_model = "checkpoints/23.pth"
    
    train_batch_size = 64
    test_batch_size = 60

    epoch = 24
    optimizer = 'sgd'  # ['sgd', 'adam']
    lr = 1e-1
    lr_step = 10
    lr_decay = 0.95
    weight_decay = 5e-4
    loss = 'focal_loss' # ['focal_loss', 'cross_entropy']
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    pin_memory = True  # if memory is large, set it True to speed up a bit
    num_workers = 4  # dataloader

config = Config()
