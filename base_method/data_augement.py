import os
import cv2
import math
import random
import numpy as np
import albumentations as al

class OpticTransormation(object):
    def __init__(self):
        pass

    def add_light(self, img, lightCenter, lightStrength, lightRadius):
        """
        给图像增加光照
        :param img: cv图像
        :param lightCenter: 光源中心坐标，可以为负
        :param lightStrength:  光源强度
        :param lightRadius: 光源半径
        :return:
        """
        img_copy = img.copy()
        h, w, c = img_copy.shape
        rectStartX = max(int(lightCenter[0] - lightRadius), 0)
        rectStartY = max(int(lightCenter[1] - lightRadius), 0)
        rectEndX = min(int(lightCenter[0] + lightRadius), w)
        rectEndY = min(int(lightCenter[1] + lightRadius), h)
        for y in range(rectStartY, rectEndY):
            for x in range(rectStartX, rectEndX):
                distance = math.pow((lightCenter[0] - x), 2) + math.pow((lightCenter[1] - y), 2)
                if distance < math.pow(lightRadius, 2):
                    extra = int(lightStrength * math.pow((1.0 - math.pow(math.sqrt(distance) / lightRadius, 2)), 2))
                    # extra = int(lightStrength * norm.cdf(math.sqrt(distance) / lightRadius, loc=0, scale=1))
                    B = img[y, x][0] + extra
                    G = img[y, x][1] + extra
                    R = img[y, x][2] + extra
                    # 判断边界 防止越界
                    B = min(255, max(0, B))
                    G = min(255, max(0, G))
                    R = min(255, max(0, R))
                    img_copy[y][x] = np.uint8((B, G, R))
        return img_copy
    def motion_kernel(self, angle, d, sz=65):
        kern = np.ones((1, d), np.float32)
        c, s = np.cos(angle), np.sin(angle)
        A = np.float32([[c, -s, 0], [s, c, 0]])
        sz2 = sz // 2
        A[:, 2] = (sz2, sz2) - np.dot(A[:, :2], ((d - 1) * 0.5, 0))
        kern = cv2.warpAffine(kern, A, (sz, sz), flags=cv2.INTER_CUBIC)
        return kern
    def defocus_kernel(self, d, sz=65):
        kern = np.zeros((sz, sz), np.uint8)
        cv2.circle(kern, (sz, sz), d, 255, -1, shift=1)
        # cv2.circle(kern, (sz, sz), d, 255, -1, cv2.CV_AA, shift=1)
        kern = np.float32(kern) / 255.0
        return kern
    def blur_image(self, img, d=9, ang=5, size=65):
        # 对图像增加失焦模糊与运动模糊
        # ang = 0
        if random.random() > 0.5:
            psf = self.defocus_kernel(d, sz=size)
        else:
            psf = self.motion_kernel(ang, d, sz=size)
        psf /= psf.sum()
        im_output = cv2.filter2D(img, -1, psf)
        return im_output
    def low_resolve(self, img):
        """
        低分辨率
        :param img:
        :return:
        """
        hr, wr, c = img.shape
        core = np.random.uniform(0.2, 0.5)
        img_ = cv2.resize(img, (int(wr * core), int(hr * core)))
        img_ = cv2.resize(img_, (wr, hr))
        return img_
    def brightness(self, image, a=0.6, b=-50):
        b = random.randint(-50, 150)
        a = random.uniform(0.4, 0.8)
        dst = np.clip(image * a + b, 0, 255)
        return dst
    def darker(self, img):
        percetage = random.randint(5, 13) * 0.1
        image_copy = img
        w = img.shape[1]
        h = img.shape[0]
        # get darker
        for xi in range(0, w):
            for xj in range(0, h):
                image_copy[xj, xi, 0] = int(img[xj, xi, 0] * percetage)
                image_copy[xj, xi, 1] = int(img[xj, xi, 1] * percetage)
                image_copy[xj, xi, 2] = int(img[xj, xi, 2] * percetage)
        return image_copy
    def gaussian_noisy(self, im, mean=0.2, sigma=0.3):
        """
        对图像做高斯噪音处理
        :param im: 单通道图像
        :param mean: 偏移量
        :param sigma: 标准差
        :return:
        """
        for _i in range(len(im)):
            im[_i] += random.gauss(mean, sigma)
        return im
    def random_gaussian_noisy(self, image, mean=100, sigma=0.5):
        """
        对图像进行高斯噪声处理
        :param image:
        :return:
        """
        # 将图像转化成数组
        img = np.asarray(image)
        img.flags.writeable = True  # 将数组改为读写模式
        width, height = img.shape[:2]
        img_r = self.gaussian_noisy(img[:, :, 0].flatten(), mean, sigma)
        img_g = self.gaussian_noisy(img[:, :, 1].flatten(), mean, sigma)
        img_b = self.gaussian_noisy(img[:, :, 2].flatten(), mean, sigma)
        img[:, :, 0] = img_r.reshape([width, height])
        img[:, :, 1] = img_g.reshape([width, height])
        img[:, :, 2] = img_b.reshape([width, height])
        # return Image.fromarray(np.uint8(img))
        return img
    def AddGauss(self, img):
        '''
        增加高斯模糊
        :param img:
        :return:
        '''
        level = random.randint(1, 2)
        img = cv2.blur(img, (level * 3 + 1, level * 3 + 1))
        return img
    def random_contrast(image, limit=(-0.3, 0.3), u=0.5):
        """
        随机对比度
        :param image:
        :param limit:
        :param u:
        :return:
        """
        image = image / 225.
        if random.random() < u:
            alpha = 1.0 + random.uniform(limit[0], limit[1])
            coef = np.array([[[0.114, 0.587, 0.299]]])  # rgb to gray (YCbCr)
            gray = image * coef
            gray = (3.0 * (1.0 - alpha) / gray.size) * np.sum(gray)
            image = alpha * image + gray
            image = np.clip(image, 0., 1.)
        image = image * 225.
        return image
    def transfore(self, img):
        h, w, _ = img.shape
        dst = np.zeros((h, w, 3), np.uint8)
        for i in range(0, h):
            for j in range(0, w):
                (b, g, r) = img[i, j]
                b = 1.5 * b
                g = 1.3 * g
                if b > 255:
                    b = 255
                if g > 255:
                    g = 255
                dst[i, j] = (b, g, r)
        return dst
    def random_hue(self, image, hue_limit=(-0.1, 0.1), u=0.5):
        image = image / 225.
        if random.random() < u:
            h = int(random.uniform(hue_limit[0], hue_limit[1]) * 100)
            image = (image * 255).astype(np.uint8)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            hsv[:, :, 0] = (hsv[:, :, 0].astype(int) + h) % 180
            image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR).astype(np.float32) / 255
        image = image * 225.
        return image
    def random_guass_filter(self, image, sigma=(0, 1.2), u=0.5):
        image = image / 225.
        if random.random() < u:
            s = int(random.uniform(sigma[0], sigma[1]))
            image = cv2.GaussianBlur(image, (5, 5), s)
        image = image * 225.
        return image
    def HorizontalFlip(self, img, mask=None):
        # 水平反转
        image = al.HorizontalFlip(p=1)(image=img, mask=mask)
        return image['image']
    def RandomRotate90(self, image, mask=None):  # 旋转90度
        image1 = al.RandomRotate90(p=1)(image=image, mask=mask)
        image = image1['image']
        mask = image1['mask']
        return image
    def Blur(self, image, mask=None):  # 模糊
        if random.random() > 0.5:
            image1 = al.Blur(blur_limit=7, p=0.5)(image=image, mask=mask)
        else:
            image1 = al.MedianBlur(blur_limit=7, p=0.5)(image=image, mask=mask)
        image = image1['image']
        mask = image1['mask']
        return image
    def HueSaturationValue(self, image, mask=None):  # HSV随机变换
        image1 = al.HueSaturationValue(p=1)(image=image, mask=mask)
        image = image1['image']
        mask = image1['mask']
        return image
    def GridDistortion(self, image, mask=None):  # 光学畸变
        # image1 = al.OpticalDistortion(p=1)(image=image, mask=mask)
        image1 = al.GridDistortion(p=1)(image=image, mask=mask)
        # image1 = al.IAAPiecewiseAffine()(image=image, mask=mask)
        image = image1['image']
        mask = image1['mask']
        return image
    def IAAAdditiveGaussianNoise(self, image, mask=None):
        image1 = al.IAAAdditiveGaussianNoise(p=1)(image=image, mask=mask)
        image = image1['image']
        mask = image1['mask']
        return image
    def PadIfNeeded(self, image, mask=None):
        h, w = image.shape[0:2]
        scale = random.randint(100, 200) * 0.01
        nw, nh = int(w * scale), int(h * scale)
        image1 = al.PadIfNeeded(p=0.3, min_height=nh, min_width=nw)(image=image, mask=mask)
        image = image1['image']
        mask = image1['mask']
        return image
    def OpticalDistortion(self, image, mask=None):  # 鱼眼特效
        image1 = al.OpticalDistortion(p=1, distort_limit=2, shift_limit=0.5)(image=image, mask=mask)
        image = image1['image']
        mask = image1['mask']
        return image
    def ElasticTransform(self, image, mask=None):
        image1 = al.ElasticTransform(p=1, alpha=5, sigma=16, alpha_affine=4)(image=image, mask=mask)
        image = image1['image']
        mask = image1['mask']
        return image
    def RGBShift(self, image, mask=None):
        # 颜色抖动
        image1 = al.RGBShift(r_shift_limit=50, g_shift_limit=20, b_shift_limit=20, always_apply=False,
                                p=1)(image=image, mask=mask)
        image = image1['image']
        mask = image1['mask']
        return image
    def ShiftScaleRotate(self, image, mask=None):
        # 随机旋转，拼接
        image1 = al.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.05, rotate_limit=30, interpolation=1,
                                        border_mode=4, value=None, mask_value=None, always_apply=False, p=1)(image=image, mask=mask)
        image = image1['image']
        mask = image1['mask']
        return image

def random_optics(image, aug_type="", ratio=0.5):
    opts = OpticTransormation()
    res = image
    if aug_type == "low_resolve" and random.random() > ratio:
        res = opts.low_resolve(image)
    elif aug_type == "blur" and random.random() > ratio:
        res = opts.blur_image(image)
    elif aug_type == "darker" and random.random() > ratio:
        res = opts.darker(image)
    elif aug_type == "transfore" and random.random() > ratio:
        res = opts.transfore(image)
    elif aug_type == "AddGauss" and random.random() > ratio:
        res = opts.AddGauss(image)
    return res

if __name__ == '__main__':
    # opts = OpticTransormation()
    # im = cv2.imread("/Users/liufn/Desktop/psd_files/psd_0518_png/psd_0518_0_4_0.png")
    # for i in range(50):
    #     res = opts.GridDistortion(im)
    #     cv2.namedWindow("show", 0)
    #     cv2.imshow("show", res)
    #     cv2.waitKey(0)
    root_dir = ""
    
    