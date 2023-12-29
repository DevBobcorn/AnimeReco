# -*- coding: utf-8 -*-
import os
import os.path as osp

import torch
import torch.nn as nn
import numpy as np
from PIL import Image

from recognition.config import config as conf
from recognition.model import FaceMobileNet, ResIRSE

def process_and_featurize(image, transform) -> torch.Tensor:
    im = transform(image)
    
    data = im.unsqueeze(0)  # shape: (1, 3, 128, 128)
    # print(data.shape)
    data = data.to(conf.device)
    net = featurize_model.to(conf.device)
    with torch.no_grad():
        features = net(data)
        features = features.cpu().numpy()
        if len(features):
            return features[0]
        else:
            return []

print('Loading model for featurizing...')

# Network Setup
if conf.backbone == 'resnet':
    featurize_model = ResIRSE(conf.embedding_size, conf.drop_ratio).to(conf.device)
else:
    featurize_model = FaceMobileNet(conf.embedding_size).to(conf.device)

featurize_model = nn.DataParallel(featurize_model)
featurize_model.load_state_dict(torch.load(conf.test_model, map_location=conf.device))
featurize_model.eval()
