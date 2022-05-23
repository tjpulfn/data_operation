import os
import cv2
import sys
import json
import random
import hashlib
import numpy as np
# __dir__ = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(__dir__)
# sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))

class findAllFile(object):
    """
    @description : 
    找到指定目录下所有指定后缀的文件
    """
    def __init__(self):
        self.file_list = []

    def check_if_dir(self, file_path, target="g"):
        temp_list = os.listdir(file_path)
        for temp_list_each in temp_list:
            temp_path = os.path.join(file_path, temp_list_each)
            if os.path.isfile(temp_path):
                if temp_path.endswith(target):
                    self.file_list.append(temp_path)
                else:
                    continue
            else:
                self.check_if_dir(temp_path)  #loop traversal
        return self.file_list

class SplitData(object):
    """
    @description : 
    按照给定比例拆分训练集，验证集，测试集
    """
    def __init__(self, path, train_ratio=0.7, val_ratio=0.3, test_ratio=None):
        self.path = path
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = 0 if not test_ratio else test_ratio
        self.find_file = findAllFile()
    
    def img2label_paths(self, image_list):
        # Define label paths as a function of image paths
        return [os.path.splitext(x)[0] + '.txt' for x in image_list]
    
    def makedir(self, path):
        if not os.path.exists(path):
            os.makedirs(path) 

    def train_test_split(self, label_type=".txt", shuffle=True):
        """
        将所有图片拆分为训练集和验证集，测试集
        """
        image_list = self.find_file.check_if_dir(self.path)
        label_files = self.img2label_paths(image_list)
        train_dir = os.path.join(self.path, "train")
        val_dir = os.path.join(self.path, "val")
        test_dir = os.path.join(self.path, "test") if self.test_ratio != 0 else None
        self.makedir(train_dir)
        self.makedir(val_dir)
        for img_file in image_list:
            base_name = img_file.split("/")[-1]
            base = os.path.splitext(base_name)[0]
            # import pdb
            # pdb.set_trace()
            label_file = os.path.splitext(img_file)[0] + '.txt'
            if not os.path.exists(label_file):
                continue
            if random.random() < self.val_ratio:
                os.system("mv {} {}".format(img_file, os.path.join(val_dir, base + ".png")))
                os.system("mv {} {}".format(label_file, os.path.join(val_dir, base + ".txt")))
            else:
                os.system("mv {} {}".format(img_file, os.path.join(train_dir, base + ".png")))
                os.system("mv {} {}".format(label_file, os.path.join(train_dir, base + ".txt")))

class ReadLabelme(object):
    def __init__(self, json_file):
        with open(json_file) as fr:
            label_dict_ = json.load(fr)
        self.shapes = label_dict_["shapes"]
    
    def read_labels(self):
        """
        返回图片中目标的标签以及最小外界矩形
        """
        label_dict = []
        for shape in self.shapes:
            label = shape["label"]
            shape_type = shape["shape_type"]
            points = shape["points"]
            if shape_type == "rectangle":
                x1, y1, x2, y2 = points[0][0], points[0][1], points[1][0], points[1][1]
            elif shape_type == "polygon":
                x, y = [], []
                for pt in points:
                    x.append(pt[0])
                    y.append(pt[1])
                x1, y1, x2, y2 = min(x), min(y), max(x), max(y)
            label_dict.append({"label":label, "minRect":[x1, y1, x2, y2]})
        return label_dict

class RotateImgWithBox(object):
    def __init__(self):
        pass
    def rotate_xy(self, x, y, angle, cx, cy):
        """
        @description : 点(x, y)绕旋转点(cx, cy)旋转angle后的坐标
        """
        angle = angle * np.pi / 180
        x_new = (x - cx) * np.cos(angle) - (y - cy) * np.sin(angle) + cx
        y_new = (x - cx) * np.sin(angle) + (y - cy) * np.cos(angle) + cy
        return x_new, y_new
    def rotate_rndom_angle(self, image, angle, points=None, bbox=False):
        """
        @description : 将图片旋转任意角度，返回旋转之后的图片和坐标
        坐标可以返回旋转后坐标 or 旋转后的最小外界矩形
        """
        h, w = image.shape[0:2]
        c_x, c_y = w // 2, h // 2
        M = cv2.getRotationMatrix2D((c_x, c_y), -angle, 1.0)
        rotate_image = cv2.warpAffine(image, M, (w, h))
        if points is None:
            return rotate_image, None
        else:
            new_points = []
            for pts in points:
                new_pts = []
                for pt in pts:
                    new_x, new_y = self.rotate_xy(pt[0], pt[1], angle, c_x, c_y)
                    if new_x < 0 or new_y < 0:
                        return None, None
                    if new_x > w or new_y > h:
                        return None, None
                    new_pts.append([new_x, new_y])
                new_points.append(new_pts)
            if bbox:
                new_points = np.array(new_points).reshape(-1, 2)
                new_points = [[np.min(new_points[:, 0]), np.min(new_points[:, 1])], [np.max(new_points[:, 0]), np.max(new_points[:, 1])]]
            return rotate_image, new_points

def get_mdh5(file_path):
    """
    @description : 
    获取输入文件的mdh5
    """
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def crop_image_with_point(img, x1, y1, x2, y2, scale=0.2):
    """
    输入原图与图片内单个目标的位置坐标，向外扩充目标宽高的一定比例
    """
    img_h, img_w = img.shape[0:2]
    w = x2 - x1
    h = y2 - y1
    x1, x2, y1, y2 = max(0, x1 - w * scale), min(img_w, x2 + w * scale), max(0, y1 - h * scale), min( img_h, y2 + h * scale)
    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
    crop_image = img[y1:y2, x1:x2]
    return crop_image



