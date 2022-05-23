import os
import cv2
import json
import numpy as np
import argparse
from base import select_seven_points, write_label_with_PgNet, feed_data


def crop_label_seal(root_dir):
    gt_dir = '{}_crop'.format(root_dir)
    if not os.path.exists(gt_dir):
        os.makedirs(gt_dir)
    fw = open("{}_label.txt".format(root_dir), "w")
    for file_name in os.listdir(root_dir):
        # if not file_name == "51-100.json":
        #     continue
        if file_name.endswith(".json"):
            print(file_name)
            base_name = os.path.splitext(file_name)[0]
            image_dir = os.path.join(root_dir, base_name)
            json_file = os.path.join(root_dir, file_name)
            with open(json_file) as fr:
                label_dict = json.load(fr)
            img_metadata = label_dict['_via_img_metadata']
            for key in img_metadata.keys():
                # try:
                    image_dict = {}
                    name = img_metadata[key]
                    filename = name["filename"]
                    image_base_name = os.path.splitext(filename)[0]
                    # if not image_base_name == "d2a2636291768ab2c9ae5131cd6654f2":
                    #     continue
                    print(file_name, filename)
                    image_dict[filename] = {"seal": 0}
                    # seal_dict = {"seal": 0}
                    regions = name["regions"]
                    for sub_regions in regions:
                        shape_attributes = sub_regions["shape_attributes"]
                        region_attributes = sub_regions["region_attributes"]
                        type_ = region_attributes["type"]
                        number = region_attributes["number"]
                        # print(number, region_attributes["line"], region_attributes["type"])
                        if "seal" in type_ and type_["seal"] == True:
                            image_dict[filename]["seal"] += 1
                            x = shape_attributes["x"]
                            y = shape_attributes["y"]
                            w = shape_attributes["width"]
                            h = shape_attributes["height"]
                            image = cv2.imread(os.path.join(image_dir, filename))
                            flags = '.jpg'
                            if image is None:
                                image = cv2.imread(os.path.join(image_dir, filename))
                                flags = '.png'
                            img_h, img_w = image.shape[0:2]
                            x1, x2, y1, y2 = x, x + w, y, y + h
                            key = "{}_crop_{}".format(image_base_name, image_dict[filename]["seal"]) + flags
                            image_dict[filename].update({key:[[x1, y1], [x2, y2]]})
                            scale = 0.3
                            x1, x2, y1, y2 = max(0, x1 - w * scale), min(img_w, x2 + w * scale), max(0, y1 - h * scale), min( img_h, y2 + h * scale)
                            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                            w, h = x2 - x1, y2 - y1
                            if w * 3 < h or h * 3 < w:
                                continue
                            crop_image = image[y1:y2, x1:x2]
                            crop_image_name = os.path.join(gt_dir, image_base_name + "_crop_{}".format(image_dict[filename]["seal"]) + flags)
                            cv2.imwrite(crop_image_name, crop_image)
                        else:
                            all_points_x = shape_attributes["all_points_x"]
                            all_points_y = shape_attributes["all_points_y"]
                            points = np.vstack((all_points_x, all_points_y))
                            points = np.transpose(points)
                            # cv2.polylines(image, [points], False, (255, 0, 0), 5, 1)
                            new_points = select_seven_points(points, 5000, 11)
                            top_line, end_line = False, False
                            if "top_line" in region_attributes["line"].keys():
                                content = region_attributes["content"]      # 选取文本信息
                                top_line = True
                            if "end_line" in region_attributes["line"].keys():
                                end_line = True
                                content = ""
                            image_dict = feed_data(image_dict, [filename, number, content, new_points, top_line, end_line])
                    # print(image_dict)                    
                    write_label_with_PgNet(fw, image_dict)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", default="/Users/liufn/Desktop/BaiDuYun/dataset/印章/识别用/训练集/第二批_整张/印章待标注第三批20210928")
    args = parser.parse_args()
    return args
    
if __name__ == "__main__":
    args = parse_args()
    crop_label_seal(args.input_path)
    # for dir_ in os.listdir(args.input_path):
    #     if os.path.isdir(os.path.join(args.input_path, dir_)):
    #         print(os.path.join(args.input_path, dir_))
    #         crop_label_seal(os.path.join(args.input_path, dir_))