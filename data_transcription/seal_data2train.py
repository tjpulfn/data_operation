import json
import os
import cv2
import sys
import random
import numpy as np
import argparse
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))
from base_method.baseMethod import findAllFile, crop_image_with_point
from base_method.data_augement import random_optics


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def labelme2train(args):
    root_path = args.input_path
    crop_save_dir = args.save_dir
    with_x_path = os.path.join(crop_save_dir, "true_data_with#x")
    without_x_path = os.path.join(crop_save_dir, "true_data_without#x")
    makedirs(with_x_path)
    makedirs(without_x_path)
    fx = open("{}.txt".format(with_x_path), "w")
    fox = open("{}.txt".format(without_x_path), "w")
    f = findAllFile()
    image_lists = f.check_if_dir(root_path)
    idx = 0 
    for i in range(args.random_num):
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
                    if args.random_num == 0:
                        scale = 0.0
                    else:
                        scale = random.randint(0, 5) * 0.01
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

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", default="/Users/liufn/Desktop/BaiDuYun/dataset/印章/识别用/训练集/第二批_整张/印章待标注第三批20210928")
    parser.add_argument("-ra", "--random_aug", default=False)
    parser.add_argument("-rn", "--random_num", default=0)
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    save_dir = "{}_random".format(args.input_path)
    makedirs(save_dir)
    args.save_dir = save_dir
    without_x_path = labelme2train(args)
    if args.ra:
        data_random_aug(without_x_path)

if __name__ == '__main__':
    main()
    