import os
from flask import *
import glob
import base64

import detection
from detection.detector import Detector

if __name__ == '__main__':
    model = Detector()

    # identifier    tag name
    # silver_wolf   銀狼(スターレイル)
    # march_7th     三月なのか
    # stelle        星(スターレイル)
    # qingque       青雀

    folder = "qingque"

    for image_path in glob.glob(f'D:/SchoolWork/CreeperX Test/Pixiv Test/downloaded {folder}/*.*'):
        try:
            pid, image_info = detection.detect(model, image_path)

            lastDotIndex = pid.rfind('.')

            if not os.path.exists(f'pixiv_avatar/{folder}'):
                os.makedirs(f'pixiv_avatar/{folder}')

            for key, result_info in image_info.items():
                    # Insert result key before the file extension, and change extension to png
                    result_path = f'pixiv_avatar/{folder}/' + pid[:lastDotIndex] + f'_{key}' + ".png"

                    img = result_info[3][22:]

                    with open(result_path, 'wb') as f:
                        f.write(base64.b64decode(img))

                    print(f'Saving {result_path}...')
        except Exception as e:
            print(e)