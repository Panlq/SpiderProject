import tkinter
from tkinter import *
import requests
from tkinter import messagebox
import re
from PIL import Image, ImageTk
from bs4 import BeautifulSoup

"""
url : www.uustv.com

参数:
word: 风道
sizes: 60
fonts: jfcs.ttf
fontcolor: #000000
"""


def getImg():

    # 请求地址：
    url = 'http://www.uustv.com/'
    name = name_entry.get()  # 获取输入的内容
    option = var.get()       # 被选中的样式
    print(name, option)
    if not name:
        messagebox.showinfo('温馨提示', '请输入名字！')
        return
    # 构造请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    }

    data = {
        'word': name,
        'sizes': 60,
        'fonts': option,
        'fontcolor': '#000000'
    }

    # 发起post请求
    response = requests.post(url, data=data, headers=headers)
    # response.encoding = 'utf-8'   # 指定返回数据的编码格式
    print(response.encoding)
    html = response.content.decode("utf-8")
    img = re.findall(r'<div class="tu">﻿.*?src="(.*?)".*?</div>', html)[0]
    # print('img:', img)
    image_url = 'http://www.uustv.com/%s' % img
    # 下载图片
    res = requests.get(image_url).content
    with open('images/'+'{}.gif'.format(name), 'wb') as f:
        f.write(res)
    try:
        filename = './images/{}.gif'.format(name)

        bm = ImageTk.PhotoImage(file=filename)
        label2 = tkinter.Label(root, image=bm)
        label2.bm = bm
        label2.grid(row=0, column=0, columnspan=count, pady=10)
        # label2.grid(row=2,rowspan=3, columnspan=2)
    except:
        pass
    # try:
    #     # 会调用本地默认的看图软件
    #     im = Image.open('images/{}.gif'.format(name))
    #     im.show()
    #     im.close()
    # except Exception as e:
    #     print('请自行打开图片')


def get_session(session_url):
    response = requests.session().get(session_url)
    html = response.content
    soup = BeautifulSoup(html, 'lxml')
    print(soup)
    options = soup.find_all('option')   # >>返回所有的option
    """ 返回的类型都是bs4.element.Tag
    [<option value="60">60像素</option>,
     <option value="jfcs.ttf">个性签</option>,
     <option value="qmt.ttf">连笔签</option>,
     <option value="bzcs.ttf">潇洒签</option>,
     <option value="lfc.ttf">草体签</option>,
     <option value="haku.ttf">合文签</option>,
     <option value="zql.ttf">商务签</option>,
     <option value="yqk.ttf">可爱签</option>]
    """

    res = []
    for option in options:
        if option.attrs['value'] != '60':
            res.append((option.attrs.get('value'), option.get_text()))
    print(res)
    return res


if __name__ == '__main__':

    startUrl = 'http://www.uustv.com/'
    # options = get_session(startUrl)
    options = [('jfcs.ttf', '个性签'), ('qmt.ttf', '连笔签'), ('bzcs.ttf', '潇洒签'), ('lfc.ttf', '草体签'), ('haku.ttf', '合文签'), ('zql.ttf', '商务签'), ('yqk.ttf', '可爱签')]

    # GUI模块，python2.7是Tkinter
    # 创建窗口控件对象
    root = tkinter.Tk()
    root.title('pythonGUI签名设计')
    # root.geometry('600x300')
    # root.geometry('+400+200')
    root.geometry('550x360+400+200')  # 指定窗口大小，和显示的偏移量,在屏幕中显示的位置

    # 设置单选框,存储类型为字符串,options是从网上爬取下来的选项
    var = StringVar()
    var.set('jfcs.ttf')   # 设置一个默认的选项
    count = 0
    for mode, text in options:
        b = Radiobutton(master=root, text=text, variable=var, value=mode)
        b.grid(row=1, column=count)
        count += 1

    # 文本输入框在第二行开始
    label = tkinter.Label(root, text='姓名：', font=('微软雅黑', 15))
    label.grid(row=2, column=0, pady=5)
    # 创建文本框
    name_entry = tkinter.Entry(root, font=('微软雅黑', 20))
    name_entry.grid(row=2, column=1, columnspan=6, pady=5)

    # 显示默认的图片，在第一行
    default_img = PhotoImage(file='images/蓝月亮.gif')
    label = Label(root, image=default_img)
    label.grid(row=0, column=0, columnspan=count, pady=10)

    # 设置按钮
    tkinter.Button(root, text='一键设计签名', font=('微软雅黑', 15), width='15', height='1',
                   command=getImg).grid(row=3, column=1, columnspan=5, pady=5)

    root.mainloop()  # 窗口持久化
    """
    参数或方法说明：
    Button：第一个参数都是窗口对象  command表示按钮要触发的回调函数
    Label:用来创建标签对象，
        image:表示图片标签
        text:文本标签
    
    Entry: 创建一个输入文本框
    grid表格，表示几行几列 :  
        row: 显示在第几行
        column:第几列
        columnspan:跨列合并
        rowspan:跨行合并
        pady:外边距
        ipady:内边距
        
    滚动窗口：
    text = ScrolledText(master, font=('微软雅黑'))
    text.grid(row=0,column=1, rowspan=4)
    """