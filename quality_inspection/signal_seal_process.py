import os
import cv2
import json
import numpy as np
import argparse
from base import select_seven_points, write_label_with_PgNet_old, feed_data

def seal2pgnet(root_dir):
    save_dir = "{}_crop".format(root_dir)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    fw = open("{}_label.txt".format(root_dir), "w")
    count = 1
    for sub_dir_root in os.listdir(root_dir):
        # if not sub_dir_root == "1-100":
        #     continue
        image_dir = os.path.join(root_dir, sub_dir_root)
        if not os.path.isdir(image_dir):
            continue
        json_file = '{}.json'.format(image_dir)
        with open(json_file) as fr:
            label_dict = json.load(fr)
        img_metadata = label_dict['_via_img_metadata']
        for key in img_metadata.keys():
            image_dict = {}
            sub_dir = img_metadata[key]
            image_name = sub_dir['filename']
            print(json_file, image_name)
            image = cv2.imread(os.path.join(image_dir, image_name))
            if image is None:
                continue
            count += 1
            image_dict[image_name] = {}
            regions = sub_dir["regions"]
            if len(regions) < 1:
                continue
            for sub_regions in regions:
                shape_attributes = sub_regions["shape_attributes"]
                all_points_x = shape_attributes["all_points_x"]
                all_points_y = shape_attributes["all_points_y"]
                points = np.vstack((all_points_x, all_points_y))
                points = np.transpose(points).astype(np.int32)
                # cv2.polylines(image, [points], False, (255, 0, 0), 5, 1)
                new_points = select_seven_points(points, 5000, 11)        # 平均选7个点
                region_attributes = sub_regions["region_attributes"]
                number = region_attributes["number"]
                top_line, end_line = False, False
                if "top_line" in region_attributes["line"].keys():
                    content = region_attributes["content"]      # 选取文本信息
                    top_line = True
                if "end_line" in region_attributes["line"].keys():
                    end_line = True
                    content = ""
                if "\n" in content:
                    print(image_name)
                    print("{} content 有回车".format(image_name))
                    print("修改后请重新运行")
                    exit()
                image_dict  = feed_data(image_dict, [image_name, number, content, new_points, top_line, end_line])
                for pt in new_points:
                    cv2.circle(image, (int(pt[0]), int(pt[1])), 10, (0, 222, 255), -1)
                new_points = np.array(new_points, dtype=np.int32)
                # cv2.polylines(image, [new_points], False, (255, 0, 0), 2)
                # cv2.imwrite(os.path.join(save_dir, image_name), image)
            # print(image_dict)
            write_label_with_PgNet_old(fw, image_dict)
    fw.close()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", default="/Users/liufn/Desktop/BaiDuYun/dataset/印章/训练集/识别用/训练集/第一批_单张/100")
    args = parser.parse_args()
    return args
    
if __name__ == "__main__":
    args = parse_args()
    seal2pgnet(args.input_path)
    # for dir_ in os.listdir(args.input_path):
    #     if os.path.isdir(os.path.join(args.input_path, dir_)):
    #         print(os.path.join(args.input_path, dir_))
    #         seal2pgnet(os.path.join(args.input_path, dir_))
