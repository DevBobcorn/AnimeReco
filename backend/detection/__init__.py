import os, cv2
from datetime import datetime

def get_filename(path):
    return os.path.split(path)[1]


def split_filename(fullname):
    names = fullname.rsplit('.', 1)
    # Base name and extension name
    return (names[0], names[1])


def detect(model, org_path, out_path, image_name):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] Processing {image_name}...')
    input_img = cv2.imread(f'{org_path}/{image_name}')

    output_image, image_info = model.detect(input_img)

    cv2.imwrite(f'{out_path}/{image_name}', output_image)
    return image_info
