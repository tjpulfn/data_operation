

"""
@description : 
使用RPA生成的数据，部分标注后，生成labelme标注格式，后生成pgnet输入格式
"""
from cProfile import label
import os
import json
import cv2
import math
import pprint
import glob
import random
import numpy as np
from PIL import Image, ImageFont, ImageDraw, ImageFilter
# from data_preprocess import rotate_rndom_angle
import sys
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))
from data_aug.rotate_img import rotate_rndom_angle
import uuid
import time
def change_name():
    image_path = '/Users/liufn/Desktop/BaiDuYun/dataset/印章/识别用/生成数据/第一批_350/911201125877383612_门诊收费专用章_6'
    label_path = '{}'.format(image_path)
    save_dir = '{}a'.format(image_path)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    for image_file in os.listdir(image_path):
        if image_file.endswith('.png'):
            index = str(uuid.uuid1())
            base_name = os.path.splitext(image_file)[0]
            label_file = os.path.join(label_path, base_name + '.json')
            new_name = '{}'.format(index)
            image = cv2.imread(os.path.join(image_path, image_file))
            os.system(
                'mv {} {}'.format(os.path.join(image_path, image_file), os.path.join(save_dir, str(new_name) + '.png')))
            # cv2.imwrite(os.path.join(save_dir, str(new_name) + '.png'), image)
            os.system('mv {} {}'.format(label_file, os.path.join(save_dir, str(new_name) + '.json')))
            # index += 1
            

def fakeData2Labelme():
    ori_json = "/Users/liufn/Desktop/BaiDuYun/生成印章原始数据/batch2/12_18_5_0/之充顺塚嗻郓肣湮呵荪抜_www.395.net.cn_alpha.json"
    with open(ori_json) as fr:
        label_dict = json.load(fr)
    ori_shapes = label_dict["shapes"]
    image_dir = "/Users/liufn/Desktop/BaiDuYun/生成印章原始数据/batch2/12_18_5_0"
    for image_file in os.listdir(image_dir):
        if image_file.endswith('g'):
            image = cv2.imread(os.path.join(image_dir, image_file))
            base_name = os.path.splitext(image_file)[0]
            print(base_name)
            h, w = image.shape[0:2]
            labelme_dict = {"version": "4.5.7", "flags": {}}
            json_file = open(os.path.join(image_dir, base_name + '.json'), 'w', encoding="utf-8")
            shapes = []
            for sub_shape in ori_shapes:
                sub_label = sub_shape["label"]
                sub_points = sub_shape["points"]
                angle = 0
                _, sub_points = rotate_rndom_angle(image, angle, [sub_points])
                shapes.append({"label": sub_label, "points": sub_points[0], "group_id": None, "shape_type": "polygon", "flags": {}})
            labelme_dict.update({"shapes": shapes})
            labelme_dict.update({"imagePath": "{}.png".format(base_name)})
            labelme_dict.update({"imageData": None})
            labelme_dict.update({"imageHeight": h})
            labelme_dict.update({"imageWidth": w})
            json_str = json.dumps(labelme_dict, indent=4)
            json_file.write(json_str)

def add_alpha_channel(img):
    """ 为jpg图像添加alpha通道 """
    b_channel, g_channel, r_channel = cv2.split(img) # 剥离jpg图像通道
    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255 # 创建Alpha通道
    img_new = cv2.merge((b_channel, g_channel, r_channel, alpha_channel)) # 融合通道
    return img_new

def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b

def fakeData2PgNet(fw):
    bg_image_list = glob.glob("/mnt/resource/liufn/code/seal_erase/document_images" + "/*g")
    img_wl = Image.open("/mnt/resource/liufn/code/data_operation/data_generate/wenli.png")
    image_dir = '/mnt/resource/liufn/datasets/trocr/stamp/fake_seal_py/save_stamp1/'
    image_list = glob.glob(image_dir  + "/*/*.png")
    save_dir = "/mnt/resource/liufn/datasets/trocr/stamp/fake_seal_py/train1"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for img_file in image_list:
        label_file = img_file.replace(".png", ".txt")
        with open(label_file) as fr:
            value = fr.readlines()[0]
        bgImgae = cv2.imread(random.choice(bg_image_list), cv2.IMREAD_UNCHANGED)
        if bgImgae.shape[-1] == 3:
            bgImgae = add_alpha_channel(bgImgae)
        h, w = bgImgae.shape[0:2]
        crop_name = str(uuid.uuid1())
        image = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)
        hg, wg = image.shape[0:2]
        if random.random() > 0:
            scale = random.randint(4,8) * 0.1
            image = cv2.resize(image, (int(wg * scale), int(hg * scale)))
            hg, wg = image.shape[0:2]
        if random.random() > 0.3 and(np.abs(hg - wg) < 30):
            angle = random.randint(0, 359)
            image, _ = rotate_rndom_angle(image, angle, points=None, bbox=False)
            hg, wg = image.shape[0:2]
        if random.random() > 0.1:
            image = Image.fromarray(image.astype('uint8')).convert('RGBA')
            pos_random = (random.randint(0, 200), random.randint(0, 100))
            box = (pos_random[0], pos_random[1], pos_random[0]+300, pos_random[1]+300)
            img_wl_random = img_wl.crop(box).rotate(random.randint(0, 360))
            # 重新设置im2的大小，并进行一次高斯模糊
            img_wl_random = img_wl_random.resize(image.size).convert('L').filter(ImageFilter.GaussianBlur(1))
            # 将纹理图的灰度映射到原图的透明度，由于纹理图片自带灰度，映射后会有透明效果，所以fill的透明度不能太低
            L, H = image.size
            for hi in range(H):
                for l in range(L):
                    dot = (l, hi)
                    image.putpixel(dot, image.getpixel(dot)[:3]+(int(img_wl_random.getpixel(dot)/255*image.getpixel(dot)[3]),))
            # import pdb
            # pdb.set_trace()
            image = np.array(image)
            hg, wg = image.shape[0:2]
        if random.random() > 0.3:
            h_ = random.randint(355,365)%360
            s = random.randint(150,250)/255.0
            v = random.randint(180,250)/255.0
            r,g,b = hsv2rgb(h_,s,v)
            # print("1", b, g, r)
            _,_,_,a = cv2.split(image)
            dic = {}
            # import pdb
            # pdb.set_trace()
            for i in range(hg):
                for j in range(wg):
                    r,g,b = hsv2rgb(h_,s,v)
                    b = int((1 + random.normalvariate(0,1)*0.05)*b)
                    g = int((1 + random.normalvariate(0,1)*0.05)*g)
                    r = int((1 + random.normalvariate(0,1)*0.05)*r)
                    b = min(max(b,0),255)
                    g = min(max(g,0),255)
                    r = min(max(r,0),255)
                    image[i, j, :] = [b, g, r, a[i, j]]
            hg, wg = image.shape[0:2]
        x1, y1 = random.randint(1, w - wg), random.randint(1, h - hg)
        x2 = x1 + image.shape[1]
        y2 = y1 + image.shape[0]
        res_img, y1, y2, x1, x2 = merge_img(bgImgae, image, y1, y2, x1, x2)
        res_h, res_w = y2 - y1, x2 - x1
        crop_scale = 0.08
        crop_x1, crop_y1, crop_x2, crop_y2 = x1 - res_w * crop_scale, y1 - res_h * crop_scale, x2 + res_w * crop_scale, y2 + res_h * crop_scale
        crop_x1, crop_y1, crop_x2, crop_y2 = map(int, [crop_x1, crop_y1, crop_x2, crop_y2])
        crop_x1, crop_y1, crop_x2, crop_y2 = max(0, crop_x1), max(0, crop_y1), min(crop_x2, res_img.shape[1] - 1), min(crop_y2, res_img.shape[0] - 1)
        crop_image = res_img[crop_y1:crop_y2, crop_x1:crop_x2]
        cv2.imwrite(os.path.join(save_dir, crop_name + ".png"), crop_image)
        with open(os.path.join(save_dir, crop_name + ".txt"), "a") as fw1:
            fw1.write(value)
        fw.write(crop_name + ".png\t" + value + "\n")

def merge_img(jpg_img, png_img, y1, y2, x1, x2):
    # 判断jpg图像是否已经为4通道
    if jpg_img.shape[2] == 3:
        jpg_img = add_alpha_channel(jpg_img)
    yy1 = 0
    yy2 = png_img.shape[0]
    xx1 = 0
    xx2 = png_img.shape[1]
 
    if x1 < 0:
        xx1 = -x1
        x1 = 0
    if y1 < 0:
        yy1 = - y1
        y1 = 0
    if x2 > jpg_img.shape[1]:
        xx2 = png_img.shape[1] - (x2 - jpg_img.shape[1])
        x2 = jpg_img.shape[1]
    if y2 > jpg_img.shape[0]:
        yy2 = png_img.shape[0] - (y2 - jpg_img.shape[0])
        y2 = jpg_img.shape[0]
 
    # 获取要覆盖图像的alpha值，将像素值除以255，使值保持在0-1之间
    alpha_png = png_img[yy1:yy2,xx1:xx2,3] / 255.0
    alpha_jpg = 1 - alpha_png
    alpha = 0.95
    beta = 1-alpha
    gamma = 8
    # 0.95, 1-0.95, 8
    # print(alpha, beta, gamma)
    # 开始叠加
    for c in range(0,3):
        jpg_img[y1:y2, x1:x2, c] = ((alpha_jpg*jpg_img[y1:y2,x1:x2,c]) + (alpha_png*png_img[yy1:yy2,xx1:xx2,c]))
        # jpg_img[y1:y2, x1:x2, c] = cv2.addWeighted((alpha_jpg*jpg_img[y1:y2,x1:x2,c]), alpha, (alpha_png*png_img[yy1:yy2,xx1:xx2,c]), beta, gamma)
        # jpg_img[y1:y2, x1:x2, c] = cv2.addWeighted((jpg_img[y1:y2,x1:x2,c]), alpha, (png_img[yy1:yy2,xx1:xx2,c]), beta, gamma)

    return jpg_img, y1, y2, x1, x2


fw = open("/mnt/resource/liufn/datasets/trocr/stamp/fake_seal_py/train1.txt", "w")
for i in range(1):
    fakeData2PgNet(fw)
# with open("/mnt/resource/liufn/datasets/trocr/stamp/fake_seal_py/save_stamp1/stamp_6char_1000.txt") as fr:
#     fr_lines = fr.readlines()
# for line in fr_lines:
#     name, label = line.strip().split("\t")
#     base_name = os.path.splitext(name)[0]
#     with open(os.path.join("/mnt/resource/liufn/datasets/trocr/stamp/fake_seal_py/save_stamp1/stamp_6char_1000", base_name + ".txt"), "w") as fw:
#         fw.write(label)
# dirs = "/mnt/resource/liufn/datasets/trocr/stamp/true_data/true_seal_data/true_data_without#x/test_data"
# # save_dir = "/mnt/resource/liufn/datasets/trocr/stamp/true_data/true_seal_data/true_data_without#x/test_data"
# # if not os.path.exists(save_dir):
# #     os.makedirs(save_dir)
# with open("/mnt/resource/liufn/datasets/trocr/stamp/true_data/true_seal_data/true_data_without#x/test_data.txt", "w") as fw:
#     for files in os.listdir(dirs):
#         if files.endswith("txt"):
#             base_name = os.path.splitext(files)[0]
#             # txt_file = os.path.join(dirs, base_name + ".txt")
#             # print(txt_file)
#             # if not os.path.exists(txt_file):
#             #     continue
#             # if random.random() > 0.9:
#             #     print(base_name)
#             #     os.system("mv {} {}".format(os.path.join(dirs, files), os.path.join(save_dir, files)))
#             #     os.system("mv {} {}".format(txt_file, os.path.join(save_dir, base_name + ".txt")))
#             with open(os.path.join(dirs, files)) as fr:
#                 fr_lines = fr.readlines()
#             for line in fr_lines:
#                 if line == "\n":
#                     continue
#                 fw.write(files + "\t" + line.strip() + "\n")
