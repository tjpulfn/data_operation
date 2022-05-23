from fileinput import filename
import os
import time
import random

def random_time():
    a1=(1900,1,1,0,0,0,0,0,0)    #设置开始日期时间元组（2020-04-12 00：00：00）
    a2=(2099,12,31,0,0,0,0,0,0)    #设置结束日期时间元组（2020-04-13 00：00：00）
    start=time.mktime(a1)    #生成开始时间戳
    # print("start时间戳:", start)
    end=time.mktime(a2)      #生成结束时间戳
    # print("end时间戳:", end)
    #随机生成10个日期字符串
    t=random.randint(start,end)    #在开始和结束时间戳中随机取出一个
    date_touple=time.localtime(t)           #将时间戳生成时间元组
    date_str=time.strftime("%Y-%m-%d %H:%M:%S",date_touple)   #将时间元组转成格式化字符串（1976-05-21）
    return date_str.split(" ")[0].replace("-", ".")

def get_words_char(count):
    ss = list("0123456789QAZXSWEDCVFRTGBNHYUJMKIOLP")
    res = ""
    for i in range(count):
        res += random.choice(ss)
    return res

def get_words_digits(count):
    ss = list("0123456789")
    res = ""
    for _ in range(count):
        res += random.choice(ss)
    return res

def read_all_files():
    lines_dict = {}
    for i in range(0, 22):
        file_path = "/Users/liufn/python/data_operation/data_generate/company_files/all_company_{}.txt".format(i)
        if os.path.exists(file_path):
            with open(file_path) as fr:
                fr_lines = fr.readlines()
                lines_dict.update({i:fr_lines})
    return lines_dict

def write_signle_files(root_path):
    with open("{}.txt".format(root_path)) as fr:
        fr_lines = fr.readlines()
    for line in fr_lines:
        name, label = line.strip().split("\t")
        base_name = os.path.splitext(name)[0]
        with open(os.path.join(root_path, base_name + ".txt"), "w") as fw:
            fw.write(label)

def write_global_files(root_path):
    with open("{}.txt".format(root_path), "w") as fw:
        for file_name in os.listdir(root_path):
            if file_name.endswith("g"):
                base_name = os.path.splitext(file_name)[0]
                with open(os.path.join(root_path, base_name + ".txt")) as fr:
                    fr_line = fr.readline()
                fw.write(file_name + "\t" + fr_line + "\n")

write_global_files("/Users/liufn/Desktop/BaiDuYun/dataset/印章/训练集/识别用/训练集/五一后/印章标注labelme5490张_random/true_data_without#x_aug")