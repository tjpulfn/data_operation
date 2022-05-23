from itertools import count
import os
import cv2
import sys
import json
import time
import numpy as np
import argparse

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))
from base_method.baseMethod import findAllFile
from quality_inspection.base import select_seven_points, write_label_with_PgNet, feed_data

def write_labelme(gt_dir, label_dict, image):
    labelme_dict = {"version": "4.0.0", "flags": {}, "imageData": None}
    h, w = image.shape[0:2]
    labelme_dict.update({"imageHeight": h})
    labelme_dict.update({"imageWidth": w})
    shapes = []
    for image_name in label_dict.keys():
        base_name = os.path.splitext(image_name)[0]
        labelme_dict.update({"imagePath": "{}".format(image_name)})
        cv2.imwrite(os.path.join(gt_dir,image_name), image)    
        seal_num = label_dict[image_name]["seal"]
        base_name = os.path.splitext(image_name)[0]
        for i in range(seal_num):
            sub_seal_name = "{}_crop_{}.jpg".format(base_name, i + 1)
            seal_points = label_dict[image_name][sub_seal_name]
            seal_points = np.array(seal_points)
            seal_dict = [seal_points.tolist()]
            x1, y1, x2, y2 = seal_points[0][0], seal_points[0][1], seal_points[1][0], seal_points[1][1] 
            for num in label_dict[image_name].keys():
                if num == "seal":
                    continue
                if base_name in num:
                    continue
                content = label_dict[image_name][num]["content"]
                top_line = label_dict[image_name][num]["top_line"].tolist()
                end_line = label_dict[image_name][num]["end_line"].tolist()
                points = top_line + end_line
                points1 = np.array(points)
                min_x, max_x, min_y, max_y = min(points1[:,0]), max(points1[:,0]), min(points1[:,1]), max(points1[:,1])
                if min_x > x1 and max_x < x2 and min_y > y1 and max_y < y2:
                    seal_dict.append({"transcription": content})
            labels = [d["transcription"] for d in seal_dict[1:]]
            shapes.append({"label": "$$".join(labels), "points": seal_dict[0], "group_id": None, "shape_type": "rectangle", "flags": {}})
        labelme_dict.update({"shapes": shapes})
        if len(shapes) < 1:
            pass
        else:
            json_file = open(os.path.join(gt_dir, base_name + '.json'), 'w', encoding='utf-8')
            json.dump(labelme_dict, json_file, ensure_ascii=False, indent=4)
    
def mutil_crop_label_seal(root_dir):
    # gt_dir = '{}_crop'.format(root_dir)
    # if not os.path.exists(gt_dir):
    #     os.makedirs(gt_dir)
    for file_name in os.listdir(root_dir):
        if file_name.endswith(".json"):
            print(file_name)
            base_name = os.path.splitext(file_name)[0]
            image_dir = os.path.join(root_dir, base_name)
            gt_dir = '{}_crop'.format(image_dir)
            if not os.path.exists(gt_dir):
                os.makedirs(gt_dir)
            json_file = os.path.join(root_dir, file_name)
            with open(json_file) as fr:
                label_dict = json.load(fr)
            img_metadata = label_dict['_via_img_metadata']
            for key in img_metadata.keys():
                    image_dict = {}
                    name = img_metadata[key]
                    filename = name["filename"]
                    dict_name = base_name + "_" + filename
                    image_base_name = os.path.splitext(dict_name)[0]
                    image_dict[dict_name] = {"seal": 0}
                    regions = name["regions"]
                    for sub_regions in regions:
                        shape_attributes = sub_regions["shape_attributes"]
                        region_attributes = sub_regions["region_attributes"]
                        type_ = region_attributes["type"]
                        number = region_attributes["number"]
                        if "seal" in type_ and type_["seal"] == True or "invoice_seal" in type_ and type_["invoice_seal"] == True:
                            image_dict[dict_name]["seal"] += 1
                            try:
                                x = shape_attributes["x"]
                                y = shape_attributes["y"]
                                w = shape_attributes["width"]
                                h = shape_attributes["height"]
                            except:
                                all_points_x = shape_attributes["all_points_x"]
                                all_points_y = shape_attributes["all_points_y"]
                                x1, x2, y1, y2 = min(all_points_x), max(all_points_x), min(all_points_y), max(all_points_y)
                                w, h = x2 - x1, y2 - y1
                            image = cv2.imread(os.path.join(image_dir, filename))
                            flags = '.jpg'
                            if image is None:
                                image = cv2.imread(os.path.join(image_dir, filename))
                                flags = '.png'
                            x1, x2, y1, y2 = x, x + w, y, y + h
                            key = "{}_crop_{}".format(image_base_name, image_dict[dict_name]["seal"]) + flags
                            image_dict[dict_name].update({key:[[x1, y1], [x2, y2]]})
                        else:
                            # print(shape_attributes)
                            all_points_x = shape_attributes["all_points_x"]
                            all_points_y = shape_attributes["all_points_y"]
                            points = np.vstack((all_points_x, all_points_y))
                            points = np.transpose(points)
                            new_points = select_seven_points(points, 5000, 11)
                            top_line, end_line = False, False
                            if "top_line" in region_attributes["line"].keys():
                                content = region_attributes["content"]      # 选取文本信息
                                top_line = True
                            if "end_line" in region_attributes["line"].keys():
                                end_line = True
                                content = ""
                            image_dict = feed_data(image_dict, [dict_name, number, content, new_points, top_line, end_line])
                    # print(image_dict)
                    write_labelme(gt_dir, image_dict, image)
                    
def signle_seal2pgnet(root_dir):
    label_file = "{}_label.txt".format(root_dir)
    with open(label_file) as fr:
        fr_lines = fr.readlines()
    label_dict = {}
    for line in fr_lines:
        name, label = line.strip().split("\t")
        label_dict[name] = json.loads(label)
    save_dir = "{}_crop".format(root_dir)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    count = 1
    fal = findAllFile()
    all_images = fal.check_if_dir(root_dir)
    for image_path in all_images:
        try:
            image = cv2.imread(image_path)
            image_name = image_path.split("/")[-1]
            cv2.imwrite(os.path.join(save_dir, image_name), image)
            base_path, ext = os.path.splitext(image_path)
            base_name = os.path.splitext(image_name)[0]
            json_path = image_path.replace(ext, ".json")
            with open(json_path) as fr:
                sub_labels = json.load(fr)
            content_labels = label_dict[image_name]
            values = []
            for content_item in content_labels:
                values.append(content_item["transcription"])
            label = "$$".join(values)
            if len(sub_labels["shapes"]) < 1:
                continue
            else:
                sub_labels["imagePath"] = image_name
                sub_labels["shapes"][0]["label"] = label
                sub_labels["imageData"] = None
                new_json = open(os.path.join(save_dir, base_name + '.json'), 'w', encoding='utf-8')
                json.dump(sub_labels, new_json, ensure_ascii=False, indent=4)
        except Exception as e:
            print(e)

def txt_to_labelme(root_dir):
    label_file = "/Users/liufn/Desktop/BaiDuYun/dataset/印章/训练集/识别用/训练集/五一前/images_true.txt"
    save_dir = "/Users/liufn/Desktop/BaiDuYun/dataset/印章/训练集/识别用/训练集/wuyiqian"
    with open(label_file) as fr:
        fr_lines = fr.readlines()
    label_dict = {}
    for line in fr_lines:
        print(line)
        name, label = line.strip().split("\t")
        label_dict[name] = label
    fal = findAllFile()
    all_images = fal.check_if_dir(root_dir)
    count = 0
    for image_path in all_images:
        try:
            # image = cv2.imread(image_path)
            image_name = image_path.split("/")[-1]
            # cv2.imwrite(os.path.join(save_dir, image_name), image)
            dir_path = "/".join(image_path.split("/")[:-1])
            base_path, ext = os.path.splitext(image_path)
            base_name = os.path.splitext(image_name)[0]
            if base_name + "_crop0_0.png" in label_dict.keys():
                json_path = image_path.replace(ext, ".json")
                os.system("mv {} {}".format(image_path, os.path.join(save_dir, image_name)))
                os.system("mv {} {}".format(json_path, os.path.join(save_dir, base_name + ".json")))
                # with open(json_path) as fr:
                #     sub_labels = json.load(fr)
                # shapes = sub_labels["shapes"]
                # for i in range(len(shapes)):
                #     key = base_name + "_crop{}_0.png".format(i)
                #     if key not in label_dict.keys():
                #         continue
                #     values = label_dict[base_name + "_crop{}_0.png".format(i)]
                #     if values != shapes[i]["label"]:
                #         print(json_path)
                #         print(os.path.join(dir_path, base_name + '.json'))
                #         print(values)
                #         print(shapes[i]["label"])
                #         print()
                #         count += 1
                #         sub_labels["shapes"][i]["label"] = values
                #         new_json = open(os.path.join(dir_path, base_name + '.json'), 'w', encoding='utf-8')
                #         json.dump(sub_labels, new_json, ensure_ascii=False, indent=4)
        except Exception as e:
            print(e)
    print(count)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", default="/Users/liufn/Desktop/BaiDuYun/dataset/印章/e2e评测集/")
    args = parser.parse_args()
    return args
    
if __name__ == "__main__":
    args = parse_args()
    mutil_crop_label_seal(args.input_path)
    # for dir_ in os.listdir(args.input_path):
    #     if os.path.isdir(os.path.join(args.input_path, dir_)):
    #         print(os.path.join(args.input_path, dir_))
    #         signle_seal2pgnet(os.path.join(args.input_path, dir_))