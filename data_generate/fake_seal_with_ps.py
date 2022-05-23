import os
import sys
import time
import random
from psd_tools import PSDImage
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '..')))

from data_generate.make_random_string import random_time, read_all_files


def fake_txt_file():
    lines_dict = read_all_files()
    with open("psd_test.txt", "w") as fw:
        fw.write("text1\ttext2\ttext3\ttext4\ttext5\n")
        for i in range(5):
            text1 = random.choice(lines_dict[8]).strip()
            text2 = random_time()
            text3 = random_time()
            text4 = random.choice(lines_dict[8]).strip()
            text5 = random.choice(lines_dict[8]).strip()
            write_str = f"{text1}\t{text2}\t{text3}\t{text4}\t{text5}\n"
            print(write_str)
            fw.write(write_str)


def fake_png_from_psd(psd_dir):
    psd_png_dir = "{}_png".format(psd_dir)
    if not os.path.exists(psd_png_dir):
        os.makedirs(psd_png_dir)
    with open("/Users/liufn/python/data_operation/data_generate/psd_test_squr0.txt") as fr:
        fr_lines = fr.readlines()
    fw = open("{}_png.txt".format(psd_dir), "w")
    idx = 1
    for line in fr_lines[idx:]:
        try:
            print(idx, line)
            # text1, text2, text3, text4, text5, text6, text7, text8, text9, text10, text11, text12, text13, text14, text15, text16 = line.strip().split("\t")
            text1, text2, text3, text4_1, text4_2, text5_1, text5_2,text6_1, text6_2, text7 = line.strip().split("\t")
            psd_file = os.path.join(psd_dir, "psd_0519_rect_{}.psd".format(idx))
            if not os.path.exists(psd_file):
                idx += 1
                continue
            psd = PSDImage.open(psd_file)
            layer_count = 0
            for layer in psd:
                if layer.is_group():
                    layer_image = layer.composite()
                    layer_name = layer.name
                    layer_image.save(f'{psd_png_dir}/psd_0519_rect_{idx}_{layer_count}.png')
                    layer_count += 1
            fw.write("psd_0519_rect_{}_0.png\t{}\n".format(idx, text1.replace(" ", "")))
            fw.write("psd_0519_rect_{}_1.png\t{}\n".format(idx, text2.replace(" ", "")))
            fw.write("psd_0519_rect_{}_2.png\t{}\n".format(idx, text3.replace(" ", "")))
            fw.write("psd_0519_rect_{}_3.png\t{}\n".format(idx, text4_1.replace(" ", "") + text4_2.replace(" ", "")))
            fw.write("psd_0519_rect_{}_4.png\t{}\t{}\n".format(idx, text6_1.replace(" ", "") + text6_2.replace(" ", ""), text7.replace(" ", "")))
            fw.write("psd_0519_rect_{}_5.png\t{}\n".format(idx, text5_1.replace(" ", "") + text5_2.replace(" ", "")))
            idx += 1
        except Exception as e:
            print(e)
            idx += 1
            pass

