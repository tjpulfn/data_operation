import os
import random
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
            label_file = os.path.splitext(img_file)[0] + '.txt'
            if not os.path.exists(label_file):
                continue
            if random.random() < self.val_ratio:
                os.system("mv {} {}".format(img_file, os.path.join(val_dir, base_name + ".png")))
                os.system("mv {} {}".format(label_file, os.path.join(val_dir, base_name + ".txt")))
            else:
                os.system("mv {} {}".format(img_file, os.path.join(train_dir, base_name + ".png")))
                os.system("mv {} {}".format(label_file, os.path.join(train_dir, base_name + ".txt")))

path = "/mnt/resource/liufn/datasets/labelme_data/seal_detect/images"
sp = SplitData(path, train_ratio=0.9, val_ratio=0.1)
sp.train_test_split()