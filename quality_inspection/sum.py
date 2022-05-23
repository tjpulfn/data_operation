import json
import os
import argparse

def cal_num_signal(input_path):
    fw = open("{}_num.txt".format(input_path), "w")
    all_seal = 0
    all_top, all_end = 0, 0
    for json_name in os.listdir(input_path):
        if json_name.endswith('.json'):
            top_num, end_num = 0, 0
            json_file = os.path.join(input_path, json_name)
            json_content = json.loads(open(json_file).read())
            sub_seal = len(json_content["_via_img_metadata"])
            for file_name, annotation in json_content["_via_img_metadata"].items():
                print(file_name)
                for region in annotation["regions"]: 
                    region_attributes = region["region_attributes"]
                    line = region_attributes["line"]
                    if "top_line" in line and line["top_line"] == True:
                        top_num += 1
                    if "end_line" in line and line["end_line"] == True:
                        end_num += 1
            all_seal += sub_seal
            all_top += top_num
            all_end += end_num
            fw.write("{},\t 一共有{}个文件(印章),\t top_line数量:{},\t end_line数量:{}\n".format(json_name, len(json_content["_via_img_metadata"]), top_num, end_num))
    fw.write("\n###############################\n整个文件夹:")
    fw.write("{}\t, 一共有{}个文件(印章)\t, top_line数量:{}\t, end_line数量:{}\n".format(input_path, all_seal, all_top, all_end))        
    print("Result file in {}_num.txt".format(input_path))


def cal_num_mutil(input_path):
    fw = open("{}_num.txt".format(input_path), "w")
    all_file = 0
    all_seal = 0
    all_invoice_seal = 0
    all_top, all_end = 0, 0
    for json_name in os.listdir(input_path):
        if json_name.endswith('.json'):
            top_num, end_num = 0, 0
            json_file = os.path.join(input_path, json_name)
            with open(json_file) as fr:
                label_dict = json.load(fr)
            sub_file = len(label_dict["_via_img_metadata"])
            seal_num = 0
            invoice_seal = 0
            top_num, end_num = 0, 0
            for _, name in label_dict["_via_img_metadata"].items():
                regions = name["regions"]
                for sub_regions in regions:
                    region_attributes = sub_regions["region_attributes"]
                    line = region_attributes["line"]
                    type_ = region_attributes["type"]
                    if "seal" in type_ and type_["seal"] == True:
                        seal_num += 1
                    elif "invoice_seal" in type_ and type_["invoice_seal"] == True:
                        invoice_seal += 1
                        seal_num += 1
                    else:
                        if "top_line" in line and line["top_line"] == True:
                            top_num += 1
                        if "end_line" in line and line["end_line"] == True:
                            end_num += 1 
            all_file += sub_file
            all_seal += seal_num
            all_top += top_num
            all_end += end_num
            all_invoice_seal += invoice_seal
            fw.write("{},\t 一共有{}个文件,\t 一共有{}个印章(其中invoice_seal类型印章有{}个)\t top_line数量:{},\t end_line数量:{}\n".format(json_name, len(label_dict["_via_img_metadata"]), seal_num, invoice_seal, top_num, end_num))          
    fw.write("\n###############################\n整个文件夹:")
    fw.write("{}\t, 一共有{}个文件\t, 一共有{}个印章(其中invoice_seal类型印章有{}个),\t top_line数量:{}\t, end_line数量:{}\n".format(input_path, all_file, all_seal, all_invoice_seal, all_top, all_end ))        
    print("Result file in {}_num.txt".format(input_path))



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", default="")
    parser.add_argument("-f", "--flag", default="")
    args = parser.parse_args()
    return args
    
if __name__ == "__main__":
    args = parse_args()
    if args.flag == "signal":
        cal_num_signal(args.input_path)
    elif args.flag == "mutil":
        cal_num_mutil(args.input_path)
    else:
        print("输入错误, 请检查")