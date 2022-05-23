import os
import cv2
import sys
import json
import numpy as np
import argparse
import random
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))
from base_method.baseMethod import findAllFile
from data_aug.crop import crop_image_with_point
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--save", default=False)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    root_dir = "/Users/liufn/Desktop/BaiDuYun/dataset/印章/训练集/识别用/训练集/五一前/第四批_整张/images_4"
    # save_dir1 = "/Users/liufn/Desktop/BaiDuYun/dataset/印章/训练集/识别用/训练集/五一前/images_nolabel"
    save_dir = "/Users/liufn/Desktop/BaiDuYun/dataset/印章/训练集/识别用/训练集/五一前/images4"
    fw = open("{}.txt".format(save_dir), "w")
    # os.makedirs(save_dir, exist_ok=False)
    # os.makedirs(save_dir1, exist_ok=False)
    fal = findAllFile()
    all_images = fal.check_if_dir(root_dir)
    count = 0
    for image_path in all_images:
        image = cv2.imread(image_path)
        image_name = image_path.split("/")[-1]
        base_path, ext = os.path.splitext(image_path)
        base_name = os.path.splitext(image_name)[0]
        json_path = image_path.replace(ext, ".json")
        if not os.path.exists(json_path):
            count += 1
            # os.system("mv {} {}".format(image_path, os.path.join(save_dir1, image_name)))
            continue
        with open(json_path) as fr:
            sub_labels = json.load(fr)
        shapes = sub_labels["shapes"]
        for i in range(len(shapes)):
            values = shapes[i]["label"]
            points = shapes[i]["points"]
            x1, y1 = min(points[0][0], points[1][0]), min(points[0][1], points[1][1])
            x2, y2 = max(points[0][0], points[1][0]), max(points[0][1], points[1][1])
            scale = random.randint(0, 5) * 0.01
            scale = 0.0
            crop_im = crop_image_with_point(image, x1, y1, x2, y2, scale=scale)
            cv2.imwrite(os.path.join(save_dir, base_name + "_crop{}_{}.png".format(i, str(scale)[-1])), crop_im)
            fw.write("{}\t{}\n".format(base_name + "_crop{}_{}.png".format(i, str(scale)[-1]), values))
            with open(os.path.join(save_dir, base_name + "_crop{}_{}.txt".format(i, str(scale)[-1])), "w") as fwi:
                fwi.write(values)
    print(count, len(all_images))