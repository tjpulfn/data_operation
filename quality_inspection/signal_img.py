import json
import os
import argparse
def signal_image(input_path):
    fw = open("{}_mis.txt".format(input_path), "w")
    for json_name in os.listdir(input_path):
        # print(json_name)
        if json_name.endswith('.json'):
            json_file = os.path.join(input_path, json_name)
            json_content = json.loads(open(json_file).read())
            for file_name, annotation in json_content["_via_img_metadata"].items():
                print(json_name, file_name)
                num_dict = {}
                top_num, end_num = 0, 0
                for region in annotation["regions"]: 
                    shape_attributes = region["shape_attributes"]
                    region_attributes = region["region_attributes"]
                    content = region_attributes["content"]
                    number = region_attributes["number"]  
                    if number in num_dict.keys():
                        num_dict[number] += 1
                    else:
                        num_dict.update({number : 1})
                    # type_ = region_attributes["type"]
                    line = region_attributes["line"]
                    if '" "' in content or "\n" in content:
                        fw.write("{}\t{}\t{}\n".format(json_name, file_name, "content里面有空格或者回车"))
                        continue
                    if '" "' in number or "\n" in number:
                        fw.write("{}\t{}\t{}\n".format(json_name, file_name, "number里面有空格或者回车"))
                        continue
                    try:
                        all_points_x = shape_attributes["all_points_x"]
                        all_points_y = shape_attributes["all_points_y"]
                        x1, x2, = all_points_x[0], all_points_x[-1]
                        if "top_line" in line and line["top_line"] == True:
                            top_num += 1
                            if x1 > x2:
                                # fw.write("{}\t{}\t{}\n".format(json_name, file_name, "top_line,x坐标从大到小"))
                                continue
                            if content == "":
                                fw.write("{}\t{}\t{}\n".format(json_name, file_name, "top_line没有content"))
                                continue
                        if "end_line" in line and line["end_line"] == True:
                            end_num += 1
                            if x1 < x2:
                                # fw.write("{}\t{}\t{}\n".format(json_name, file_name, "end_line,x坐标从小到大"))
                                continue
                            if content != "":
                                fw.write("{}\t{}\t{}\n".format(json_name, file_name, "end_line有content"))
                                continue
                        if not line:
                            fw.write("{}\t{}\t{}\n".format(json_name, file_name, "没有勾选line的类型"))
                            continue
                    except Exception as e:
                        fw.write("{}\t{}\t{}\n".format(json_name, file_name, "印章没有勾选"))
                        continue
                if top_num != end_num:
                    fw.write("{}\t{}\t{}\n".format(json_name, file_name, "top_line与end_line数量不相等"))
                for k, v in num_dict.items():
                    if k != 1 and v != 2:
                        fw.write("{}\t{}\t{}\n".format(json_name, file_name, "number数量不匹配"))
                        continue

    print("Result file in {}_mis.txt".format(input_path))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", default="/Users/liufn/Downloads/017001-018000-已标注/017001-018000-已标注")
    args = parser.parse_args()
    return args
    
if __name__ == "__main__":
    args = parse_args()
    signal_image(args.input_path)