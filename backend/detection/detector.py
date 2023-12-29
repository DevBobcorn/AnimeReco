import torch
import numpy as np
from models.experimental import attempt_load
from utils.general import non_max_suppression, scale_coords, letterbox
from utils.torch_utils import select_device
import cv2
from PIL import Image
from random import randint
import base64

from config import config
from recognition.featurize import process_and_featurize
from recognition.elastic_search import feature_search

class Detector(object):

    def __init__(self):
        self.img_size = 640
        self.threshold = 0.4
        self.max_frame = 160
        self.init_model()

    # 加载YoloV5 Anime的模型权重并初始化
    def init_model(self):
        self.weights = 'weights/yolov5s_anime.pt'
        self.device = '0' if torch.cuda.is_available() else 'cpu'
        self.device = select_device(self.device)
        model = attempt_load(self.weights, map_location=self.device)
        model.to(self.device).eval()
        model.half()
        # torch.save(model, 'test.pt')
        self.m = model

    # 图像预处理
    def preprocess(self, img):
        img0 = img.copy()
        img = letterbox(img, new_shape=self.img_size)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.device)
        img = img.half()  # 半精度
        img /= 255.0  # 图像归一化
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        return img0, img

    # 在图像上框出目标，并加上label
    def plot_bboxes(self, image, bboxes, line_thickness=None):
        tl = line_thickness or round(
            0.002 * (image.shape[0] + image.shape[1]) / 2) + 1  # line/font thickness
        for (x1, y1, x2, y2, label_text) in bboxes:
            # Background & Foreground colors
            # NOTE: Color channels are in BGR order!
            bg_color = [ 180, 105, 255 ]
            fg_color = [ 255, 255, 255 ]

            # 绘制目标选框
            c1, c2 = (x1, y1), (x2, y2)
            cv2.rectangle(image, c1, c2, bg_color, thickness=tl, lineType=cv2.LINE_AA) # 空心矩形

            # 绘制label
            tf = max(tl - 1, 1)  # 字体粗细
            t_size = cv2.getTextSize(label_text, 0, fontScale=tl / 3, thickness=tf)[0]
            c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
            cv2.rectangle(image, c1, c2, bg_color, -1, cv2.LINE_AA)  # 实心矩形

            cv2.putText(image, f'{label_text}', (c1[0], c1[1] - 2), 0, tl / 3,
                        fg_color, thickness=tf, lineType=cv2.LINE_AA)
        return image

    def detect(self, im):

        im0, img = self.preprocess(im)

        results = self.m(img, augment=False)[0]
        results = results.float()
        results = non_max_suppression(results, self.threshold, 0.3)

        result_bboxes = []
        image_info = {}
        index = 0
        for det in results:
            if det is not None and len(det):
                det[:, :4] = scale_coords(
                    img.shape[2:], det[:, :4], im0.shape).round()

                for *x, conf, cls_id in det:
                    x1, y1 = int(x[0]), int(x[1])
                    x2, y2 = int(x[2]), int(x[3])

                    # Make sure cropped width and height are even numbers
                    if ((x2 - x1) % 2 == 1):
                        x2 = x2 - 1
                    
                    if ((y2 - y1) % 2 == 1):
                        y2 = y2 - 1
                    
                    crop_w = x2 - x1
                    crop_h = y2 - y1

                    # make it a square
                    if crop_w > crop_h:
                        expand_h = (crop_w - crop_h) // 2
                        y1 -= expand_h
                        y2 += expand_h
                        crop_h = crop_w
                    elif crop_w < crop_h:
                        expand_w = (crop_h - crop_w) // 2
                        x1 -= expand_w
                        x2 += expand_w
                        crop_w = crop_h

                    index += 1
                    key = str(index)

                    croppedPixels = im[y1:y2, x1:x2]
                    
                    if croppedPixels.shape[0] == 0 or croppedPixels.shape[1] == 0: # Empty after adjustments, skip
                        continue

                    # Crop out detected part
                    # IMPORTANT!!! It is REQUIRED to change channel order from BGR to RGB
                    # before Converting this cv2 nparray to a PIL Image
                    cropped_image = Image.fromarray(croppedPixels[:, :, ::-1].copy()).convert('RGB')
                    # NOTE: channels in croppedBytes are still in cv2's BGR order, but this
                    # will be handled correctly with cv2's imencode method
                    croppedBytes = cv2.imencode('.png', croppedPixels)[1]

                    # Recognize the part
                    embedding = process_and_featurize(cropped_image, config.test_transform)
                    best_match = feature_search(embedding)[0]

                    best_match_label = best_match['label']
                    best_match_score = best_match['score']

                    image_base64 = 'data:image/png;base64,' + base64.b64encode(croppedBytes).decode('ascii')
                    image_info[key] = [x2-x1, y2-y1, best_match_label, best_match_score, image_base64]

                    result_bboxes.append((x1, y1, x2, y2, best_match_label))

        im = self.plot_bboxes(im, result_bboxes)
        return im, image_info
