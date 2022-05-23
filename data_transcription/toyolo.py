import os
import cv2
import sys
import json
import yaml
import argparse
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))

from base_method.baseMethod import findAllFile

"""
@description : 
将所有数据转换成yolo格式
"""
def coco_encoder(x1, y1, x2, y2, img_h, img_w):
    '''
    将原始的标注,转换为yolo格式的标注
    输入:x1, y1, x2, y2, img_h, img_w
    输出:cx,cy,w,h  在原图的比例
    '''
    gt_w, gt_h = (x2 * 1.0 - x1), (y2 * 1.0 - y1)
    gt_cx, gt_cy = x1 + gt_w / 2, y1 + gt_h / 2
    pr_cx, pr_cy, pr_w, pr_h = gt_cx / img_w, gt_cy / img_h, gt_w / img_w, gt_h / img_h
    if pr_cx < 0 or pr_cy < 0 or pr_w < 0 or pr_h < 0:
        print(x1, x2, y1, y2)
    return pr_cx, pr_cy, pr_w, pr_h


def stamp_mutil_label(image_file, ori_content, stamp_clolr, stamp_shape):
    """
    @description : 
    输入原始的标注字段,转换成多标签，现在两个标签，颜色c1，形状c2
    """
    c1, c2 = -1, -1
    if "红" in ori_content:
        c1 = stamp_clolr.index("red")
    elif "黑白" in ori_content:
        c1 = stamp_clolr.index("black")
    elif "蓝" in ori_content:
        c1 = stamp_clolr.index("blue")
    else:
        print("c1 label:", image_file, ori_content)
    if "椭圆" in ori_content:
        c2 = stamp_shape.index("ellipse") + 3
    elif "方" in ori_content:
        c2 = stamp_shape.index("rectangle") + 3
    elif "圆" in ori_content:
        c2 = stamp_shape.index("circle") + 3
    elif "菱" in ori_content:
        c2 = stamp_shape.index("diamond") + 3
    else:
        print("c2 label:", image_file, ori_content)
    return c1, c2
    
def mutil_label2yolov5(image_list, classes, data_type="stamp"):
    """
    @description : 
    输入labelme中的shapes
    labelme格式的标注。单个目标多个标签转换, 现在只有印章
    """
    stamp_color = classes["stamp_color"]
    stamp_shape = classes["stamp_shape"]
    for image_file in image_list:
        image = cv2.imread(image_file)
        h, w = image.shape[0:2]
        json_file = os.path.splitext(image_file)[0] + '.json'
        if not os.path.exists(json_file):
            continue
        with open(json_file) as fr:
            label_dict = json.load(fr)
        shapes = label_dict["shapes"]
        with open(os.path.splitext(image_file)[0] + '.txt', "w") as fw:
            for shape in shapes:
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
                cx,cy,im_w, im_h = coco_encoder(x1, y1, x2, y2, h, w)
                c1, c2 = stamp_mutil_label(image_file, label, stamp_color, stamp_shape)
                cx, cy, im_w, im_h = map(float, [cx,cy,im_w, im_h])
                c1, c2, cx,cy,im_w,im_h = map(str, [c1, c2, cx,cy,im_w, im_h])
            
                fw.write("{} {} {} {} {}\n".format(c1, cx,cy,im_w,im_h))
                fw.write("{} {} {} {} {}\n".format(c2, cx,cy,im_w,im_h))


def parse_opt(known=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', type=str, default='./data_transcription/datasets.yaml', help='model.yaml path')
    parser.add_argument('--data_type', type=str, default='stamp', help='data_type')
    opt = parser.parse_known_args()[0] if known else parser.parse_args()
    return opt

def main(opt):
    datasets = yaml.load(open(opt.cfg))
    root_dir = datasets["data_path"]
    findtools = findAllFile()
    image_list = findtools.check_if_dir(root_dir)
    mutil_label2yolov5(image_list, datasets["classes"], opt.data_type)
    

if __name__ == '__main__':
    opt = parse_opt()
    main(opt)
    