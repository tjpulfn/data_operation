import json
import os
import argparse


def mulit_img(input_path):
    fw = open("{}_mis.txt".format(input_path), "w")
    for json_name in os.listdir(input_path):
        if json_name.endswith('.json'):
            print(json_name)
            json_file = os.path.join(input_path, json_name)
            with open(json_file) as fr:
                label_dict = json.load(fr)
            for key, name in label_dict["_via_img_metadata"].items():
                print(json_name, key)
                num_dict = {}
                top_num, end_num = 0, 0
                regions = name["regions"]
                for sub_regions in regions:
                    shape_attributes = sub_regions["shape_attributes"]
                    region_attributes = sub_regions["region_attributes"]
                    type_ = region_attributes["type"]
                    line = region_attributes["line"]
                    number = region_attributes["number"]
                    if number == "":
                        continue
                    if number in num_dict.keys():
                        num_dict[number] += 1
                    else:
                        num_dict.update({number : 1})
                    content = region_attributes["content"]
                    if '" "' in content or "\n" in content:
                        fw.write("{}\t{}\t{}\n".format(json_name, key, "content里面有空格或者回车"))
                        continue
                    if '" "' in number or "\n" in number:
                        fw.write("{}\t{}\t{}\n".format(json_name, file_name, "number里面有空格或者回车"))
                        continue
                    if "seal" in type_ and type_["seal"] == True:
                        if "top_line" in line and line["top_line"] == True:
                            top_num += 1
                            fw.write("{}\t{}\t{}\n".format(json_name, key, "印章和top_line同时勾选"))
                            continue
                        if "end_line" in line and line["end_line"] == True:
                            end_num += 1
                            fw.write("{}\t{}\t{}\n".format(json_name, key, "印章和end_line同时勾选"))
                            continue
                    else:
                        try:
                            all_points_x = shape_attributes["all_points_x"]
                            # all_points_y = shape_attributes["all_points_y"]
                            x1, x2, = all_points_x[0], all_points_x[-1]
                            if "top_line" in line and line["top_line"] == True:
                                top_num += 1
                                if x1 > x2:
                                    fw.write("{}\t{}\t{}\n".format(json_name, key, "top_line,x坐标从大到小"))
                                    continue
                                if content == "":
                                    fw.write("{}\t{}\t{}\n".format(json_name, key, "top_line没有content"))
                                    continue
                            if "end_line" in line and line["end_line"] == True:
                                end_num += 1
                                if x1 < x2:
                                    fw.write("{}\t{}\t{}\n".format(json_name, key, "end_line,x坐标从小到大"))
                                    continue
                                if content != "":
                                    fw.write("{}\t{}\t{}\n".format(json_name, key, "end_line有content"))
                                    continue
                            if not line:
                                fw.write("{}\t{}\t{}\n".format(json_name, key, "没有勾选line的类型"))
                                continue
                        except:
                            fw.write("{}\t{}\t{}\n".format(json_name, key, "印章没有勾选"))
                            continue
                if top_num != end_num:
                    fw.write("{}\t{}\t{}\n".format(json_name, key, "top_line与end_line数量不相等"))
                for k, v in num_dict.items():
                    if k != '1' and v != 2:
                        fw.write("{}\t{}\t{}\n".format(json_name, key, "number数量不匹配"))
                        continue
    print("Result file in {}_mis.txt".format(input_path))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", default="")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    mulit_img(args.input_path)