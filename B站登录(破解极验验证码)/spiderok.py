# -*- coding:utf-8 -*-
"""
    环境：python3.6.0
    工具：selenium

    参考：http://cuijiahua.com/blog/2017/11/spider_2_geetest.html
"""
import time, random
import PIL.Image as image
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests, json, re, urllib
from bs4 import BeautifulSoup
from urllib.request import urlretrieve


class Crack(object):
    def __init__(self, username, passwd):
        self.url = 'https://passport.bilibili.com/login'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 100)
        self.username = username
        self.BORDER = 6
        self.passwd = passwd

    def open(self):
        """
        打开浏览器,并输入查询内容
        """
        """打开浏览器，进入登录界面,并输入用户名和密码"""
        self.browser.get(self.url)
        keyword = self.wait.until(EC.presence_of_element_located((By.ID, 'login-username')))
        keyword.send_keys(self.username)
        keyword = self.wait.until(EC.presence_of_element_located((By.ID, 'login-passwd')))
        # keyword.send_keys(self.passwd)

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(screenshot)
        return screenshot

    def get_position(self):
        """
        获取图片验证码的位置
        :return: 验证码位置元组

        """
        img = self.browser.find_element_by_class_name("gt_box")
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return top, bottom, left, right

    def get_image(self, name="captcha.png"):
        """
        获取验证码图片
        :param name: 
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码的位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def get_images(self, bg_filename='bg.jpg', fullbg_filename='fullbg.jpg'):
        """
        获取验证码图片
        :return: 图片的location信息
        """
        bg = []
        fullbg = []
        while bg == [] and fullbg == []:
            bf = BeautifulSoup(self.browser.page_source, 'lxml')
            bg = bf.find_all('div', class_='gt_cut_bg_slice')
            fullbg = bf.find_all('div', class_='gt_cut_fullbg_slice')

        print(bg)
        print(fullbg)
        print("-"*20)
        time.sleep(1)

        bg_url = re.findall(r'url\(\"(.*)\"\);', bg[0].get('style'))[0].replace('webp', 'jpg')
        print(bg_url)
        fullbg_url = re.findall(r'url\(\"(.*)\"\);', fullbg[0].get('style'))[0].replace('webp', 'jpg')
        print(fullbg_url)
        bg_location_list = []
        fullbg_location_list = []
        for each_bg in bg:
            # 提取图片的位置信息
            location = {}
            #  返回的类型 > [('-109', '0')]
            location['x'] = int(re.findall('background-position: (.*)px (.*)px;', each_bg.get('style'))[0][0])
            location['y'] = int(re.findall('background-position: (.*)px (.*)px;', each_bg.get('style'))[0][1])
            bg_location_list.append(location)
        for each_fullbg in fullbg:
            location = {}
            location['x'] = int(re.findall('background-position: (.*)px (.*)px;', each_fullbg.get('style'))[0][0])
            location['y'] = int(re.findall('background-position: (.*)px (.*)px;', each_fullbg.get('style'))[0][1])
            fullbg_location_list.append(location)

        urlretrieve(url=bg_url, filename=bg_filename)
        print('缺口图片下载完成')
        urlretrieve(url=fullbg_url, filename=fullbg_filename)
        print('背景图片下载完成')
        return bg_location_list, fullbg_location_list

    def get_merge_image(self, filename, location_list):
        """
        根据位置对图片进行合并还原
        :filename:图片
        :location_list:图片位置
        """
        im = image.open(filename)  # 读取图片
        new_im = image.new('RGB', (260, 116))   #创建新图片
        im_list_upper = []   # 图片上半部分
        im_list_down = []     # 图片下半部分

        # crop函数就是剪切 (left, upper, right, lower)设置要裁剪的区域
        for location in location_list:
            if location['y'] == -58:
                im_list_upper.append(im.crop((abs(location['x']), 58, abs(location['x']) + 10, 166)))
            if location['y'] == 0:
                im_list_down.append(im.crop((abs(location['x']), 0, abs(location['x']) + 10, 58)))

        new_im = image.new('RGB', (260, 116))

        x_offset = 0
        for im in im_list_upper:
            # 图像黏贴（合并）
            # im.paste(region,box)#粘贴box大小的region到原先的图片对象中
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        x_offset = 0
        for im in im_list_down:
            new_im.paste(im, (x_offset, 58))
            x_offset += im.size[0]

        new_im.save(filename)

        return new_im

    def is_pixel_equal(self, img1, img2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pix1 = img1.load()[x, y]
        pix2 = img2.load()[x, y]
        threshold = 60
        if (abs(pix1[0] - pix2[0] < threshold) and abs(pix1[1] - pix2[1] < threshold) and abs(
                        pix1[2] - pix2[2] < threshold)):
            return True
        else:
            return False

    def get_gap(self, img1, img2):
        """
        获取缺口偏移量
        :param img1: 不带缺口图片
        :param img2: 带缺口图片
        :return:
        """
        left = 43
        for i in range(left, img1.size[0]):
            for j in range(img1.size[1]):
                if not self.is_pixel_equal(img1, img2, i, j):
                    left = i
                    return left
        return left

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0.0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 2
            else:
                # 加速度为负3
                a = -3
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        while True:
            try:
                slider = self.browser.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")
                break
            except:
                time.sleep(0.5)
        return slider

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        while track:
            x = random.choice(track)
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
            track.remove(x)
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    def crack(self):
        # 打开浏览器
        self.open()

        # 保存的图片名字
        bg_filename = 'bg.jpg'
        fullbg_filename = 'fullbg.jpg'

        # 获取图片
        bg_location_list, fullbg_location_list = self.get_images(bg_filename, fullbg_filename)

        # 根据位置对图片进行合并还原
        bg_img = self.get_merge_image(bg_filename, bg_location_list)
        fullbg_img = self.get_merge_image(fullbg_filename, fullbg_location_list)

        # 获取缺口位置
        gap = self.get_gap(fullbg_img, bg_img)
        print('缺口位置', gap)

        track = self.get_track(gap - self.BORDER)
        print('滑动滑块')
        print(track)

        # 点按呼出缺口
        slider = self.get_slider()
        # 拖动滑块到缺口处
        self.move_to_gap(slider, track)

    def __del__(self):
        self.browser.close()


if __name__ == '__main__':
    print('开始验证')
    crack = Crack('', '')
    crack.crack()
    print('验证成功')