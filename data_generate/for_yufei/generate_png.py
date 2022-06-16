import os
import sys
import time
import random
from psd_tools import PSDImage

def fake_png_from_psd(psd_dir, psd_txt, pre_save_name, psd_save_name, idx):
    psd_png_dir = "{}_png".format(psd_dir)
    if not os.path.exists(psd_png_dir):
        os.makedirs(psd_png_dir)
    with open(psd_txt) as fr:
        fr_lines = fr.readlines()
    fw = open("{}_png.txt".format(psd_dir), "w")
    for line in fr_lines[idx:]:
        try:
            text1, text2, text3 = line.strip().split("\t")
            psd_file = os.path.join(psd_dir, "{}_{}.psd".format(psd_save_name, idx))
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
                    layer_image.save(f'{psd_png_dir}/{pre_save_name}_{idx}_{layer_count}.png')
                    layer_count += 1
            fw.write("{}_{}_0.png\t{}$${}$${}\n".format(pre_save_name, idx, text1.replace(" ", ""), text2.replace(" ", ""), text3.replace(" ", "")))
            idx += 1
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
    args = parse_args()
    psd_dir = "/Users/liufn/Desktop/psd_files/psd_test_0608_1"
    #  保存psd文件的文件夹路径
    psd_txt = "*.txt"
    #  我发的psd.txt文件，用于在photoshop中生成样本的文件
    pre_save_name = ""
    #  要保存png时的图片前缀名
    psd_save_name = ""
    #  使用photoshop保存 psd 文件时，psd文件的前缀名
    fake_png_from_psd(psd_dir, psd_txt, pre_save_name, psd_save_name, int(args.idx))
    
