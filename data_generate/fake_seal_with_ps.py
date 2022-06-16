import os
import sys
import time
import random
from psd_tools import PSDImage
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))

from data_generate.make_random_string import random_time, read_all_files, get_words_digits, get_words_char



def fake_txt_file():
    """
    @description : 
        需要改的：txt文件名----一般都是日期命名
                fw.write("text1\ttext2\ttext3\n")，有几条文字就几个text
                get_words_digits()    只拿数字,
                get_words_char()     数字+大写字母
                random_time         生成时间，
    """
    
    lines_dict = read_all_files()   ##  lines_dict 已经读出所有文件
    with open("psd_test_0615_1.txt", "w") as fw:
        fw.write("text1\ttext2\n")
        # \ttext4\ttext5\ttext6\ttext7\ttext8\ttext9\ttext10_1\ttext10_2\ttext11_1\ttext11_2\ttext12_1\ttext12_2\ttext13\ttext14\ttext15\ttext16
        for i in range(2000):
            text1 = random.choice(lines_dict[7]).strip()
            text2 = random.choice(lines_dict[7]).strip() + "(" + get_words_digits(1) + ")"
            # text2 = text2_1[0] + get_words_digits(3) + text2_1[1]
            text3 = random.choice(lines_dict[7]).strip()
            text4 = random.choice(lines_dict[5]).strip()
            text5 = random.choice(lines_dict[4]).strip()

            text6 = random.choice(lines_dict[3]).strip()
            text7 = random.choice(lines_dict[2]).strip()
            # text8 = random.choice(lines_dict[5]).strip()
            # text9 = get_words_digits(13)

            # if random.random() > 0.5:
            #     text10_1 = random.choice(lines_dict[2]).strip()
            #     text10_2 = "之印"
            # else:
            #     text10 = random.choice(lines_dict[3]).strip()
            #     text10_1 = text10[:2]
            #     text10_2 = text10[2:] + "印"

            # if random.random() > 0.5:
            #     text11_1 = random.choice(lines_dict[2]).strip()
            #     text11_2 = "之印"
            # else:
            #     text11 = random.choice(lines_dict[3]).strip()
            #     text11_1 = text11[:2]
            #     text11_2 = text11[2:] + "印"
            
            # text12_1 = random.choice(lines_dict[2]).strip()
            # text12_2 = "印"

            # text13 = random.choice(lines_dict[2]).strip()
            # text14 = random.choice(lines_dict[5]).strip()
            # text15 = random.choice(lines_dict[3]).strip()
            # text16 = get_words_digits(12)
            write_str = f"{text1}\t{text2}\t{text3}\t{text4}\t{text5}\t{text6}\t{text7}\n"
            # \t{text6}\t{text7}\t{text8}\t{text9}\t{text10}\t{text11}
            # \t{text4}\t{text5}\t{text6}\t{text7}\t{text8}\t{text9}\t{text10_1}\t{text10_2}\t{text11_1}\t{text11_2}\t{text12_1}\t{text12_2}\t{text13}\t{text14}\t{text15}\t{text16}
            print(write_str)
            fw.write(write_str)


def fake_png_from_psd(psd_dir, idx):
    psd_png_dir = "{}_png".format(psd_dir)
    if not os.path.exists(psd_png_dir):
        os.makedirs(psd_png_dir)
    with open("/Users/liufn/python/data_operation/psd_test_0608_1.txt") as fr:
        fr_lines = fr.readlines()
    fw = open("{}_png.txt".format(psd_dir), "w")
    # idx = 1360
    for line in fr_lines[idx:]:
        try:
            
            # # text1, text2, text3, text4, text5, text6, text7, text8, text9, text10, text11, text12, text13, text14, text15, text16 = line.strip().split("\t")
            text1, text2, text3 = line.strip().split("\t")
            # , text4, text5, text6, text7, text8, text9, text10_1, text10_2, text11_1, text11_2, text12_1, text12_2, text13, text14, text15, text16 
            psd_file = os.path.join(psd_dir, "psd_0608_1_{}.psd".format(idx))
            print(idx, psd_file)
            if not os.path.exists(psd_file):
                idx += 1
                continue
            psd = PSDImage.open(psd_file)
            layer_count = 0
            for layer in psd:
                if layer.is_group():
                    layer_image = layer.composite()
                    layer_name = layer.name
                    layer_image.save(f'{psd_png_dir}/psd_0608_1_{idx}_{layer_count}.png')
                    layer_count += 1
            
            fw.write("psd_0608_1_{}_0.png\t{}$${}$${}\n".format(idx, text1.replace(" ", ""), text2.replace(" ", ""), text3.replace(" ", "")))
            idx += 1
            # time.sleep(0)
        except Exception as e:
            print(e)
            idx += 1
            pass


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--idx", default=1)
    args = parser.parse_args()
    return args

import argparse

if __name__ == '__main__':
    #  生成txt
    fake_txt_file()
    #  生成png
    # args = parse_args()
    # fake_png_from_psd("/Users/liufn/Desktop/psd_files/psd_test_0608_1", int(args.idx))
    
# with open("/Users/liufn/python/data_operation/data_generate/company_files/all_seal_name.txt") as fs:
#     fs_lines = fs.readlines()
# fake_png_from_psd()

