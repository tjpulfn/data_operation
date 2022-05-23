import json
from ntpath import join
import os
from re import S
import cv2
import sys
import random
import numpy as np

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))
from base_method.baseMethod import findAllFile, crop_image_with_point
from base_method.data_augement import random_optics


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def labelme2train(root_path, crop_save_dir, random_num=1):
    with_x_path = os.path.join(crop_save_dir, "true_data_with#x")
    without_x_path = os.path.join(crop_save_dir, "true_data_without#x")
    makedirs(with_x_path)
    makedirs(without_x_path)
    fx = open("{}.txt".format(with_x_path), "w")
    fox = open("{}.txt".format(without_x_path), "w")
    f = findAllFile()
    image_lists = f.check_if_dir(root_path)
    idx = 0 
    for i in range(random_num):
        for image_file in image_lists[idx:]:
            try:
                image = cv2.imread(image_file)
                base_path_name = os.path.splitext(image_file)[0]
                base_name = image_file.split("/")[-1]
                print(idx, base_name)
                img_base_name = os.path.splitext(base_name)[0]
                if base_name.startswith("."):
                    continue
                label_file = base_path_name + ".json"
                with open(label_file) as fr:
                    labels = json.load(fr)
                shapes = labels["shapes"]
                for i, shape in enumerate(shapes):
                    flag = True
                    values = shape["label"]
                    if "#x" in values:
                        flag = False
                    points = shape["points"]
                    points = np.array(points).reshape((-1, 2))
                    x1, y1 = min(points[:, 0]), min(points[:, 1])
                    x2, y2 = max(points[:, 0]), max(points[:, 1])
                    scale = random.randint(0, 5) * 0.01
                    # scale = 0.0
                    crop_im = crop_image_with_point(image, x1, y1, x2, y2, scale=scale)
                    if flag:
                        cv2.imwrite(os.path.join(without_x_path, img_base_name + "_crop{}_{}.png".format(i, str(scale)[-1])), crop_im)
                        with open(os.path.join(without_x_path, img_base_name + "_crop{}_{}.txt".format(i, str(scale)[-1])), "w") as fwi:
                            fwi.write(values)
                        fox.write("{}\t{}\n".format(img_base_name + "_crop{}_{}.png".format(i, str(scale)[-1]), values))
                    else:
                        cv2.imwrite(os.path.join(with_x_path, img_base_name + "_crop{}_{}.png".format(i, str(scale)[-1])), crop_im)
                        with open(os.path.join(with_x_path, img_base_name + "_crop{}_{}.txt".format(i, str(scale)[-1])), "w") as fwi:
                            fwi.write(values)
                        fx.write("{}\t{}\n".format(img_base_name + "_crop{}_{}.png".format(i, str(scale)[-1]), values))
                idx += 1
            except Exception as e:
                print(e)
        
    return without_x_path

def data_random_aug(without_x_path):
    save_path = "{}_aug".format(without_x_path)
    os.makedirs(save_path, exist_ok=True)
    for image_file in os.listdir(without_x_path):
        if image_file.endswith("g"):
            base_name = os.path.splitext(image_file)[0]
            image = cv2.imread(os.path.join(without_x_path, image_file))
            aug_type = random.choice(["low_resolve", "blur", "darker", "AddGauss"])
            print(aug_type)
            res = random_optics(image, aug_type, ratio=0.0)
            cv2.imwrite(os.path.join(save_path, base_name + "_" + aug_type + ".png"), res)
            with open(os.path.join(without_x_path, base_name + ".txt")) as fr:
                fr = fr.readline()
            print(fr)
            with open(os.path.join(save_path, base_name + "_" + aug_type + ".txt"), "w") as fw:
                fw.write(fr)
def main():
    path = "/Users/liufn/Desktop/BaiDuYun/dataset/印章/训练集/识别用/训练集/五一后/印章标组labelme3409张"
    save_dir = "{}_random".format(path)
    makedirs(save_dir)
    without_x_path = labelme2train(path, save_dir, random_num=2)
    data_random_aug(without_x_path)

if __name__ == '__main__':
    main()
    