import os
import random
from PIL import Image

from recognition.featurize import process_and_featurize
from recognition.elastic_search import store_feature, feature_search

from config import config as conf

def featurize_all_labels(data_root):
    for label in os.listdir(data_root):
        # Get all images with this label
        images = os.listdir(f'{data_root}/{label}')

        # Randomly pick 10 from every label
        images = random.sample(images, 10)
        for filename in images:
            image = Image.open(f'{data_root}/{label}/{filename}')
            feature = process_and_featurize(image, conf.test_transform)

            if len(feature) > 0:
                store_feature(label, feature, filename)


def test_labels(data_root):
    # Do some queries
    for label in os.listdir(data_root):
        if not os.path.isdir(os.path.join(data_root, label)): # Skip entries which isn't a folder
            continue

        # Get all images with this label
        images = os.listdir(f'{data_root}/{label}')
        filename = random.choice(images)

        print(f'Testing label [{label}] with [{filename}]')

        image = Image.open(f'{data_root}/{label}/{filename}')
        feature = process_and_featurize(image, conf.test_transform)
        result = feature_search(feature)

        print(result)

if __name__ == '__main__':
    #featurize_all_labels(conf.train_root)
    test_labels(conf.test_root)