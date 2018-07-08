"""
测试带选择框的GUI
"""

from tkinter import *
from tkinter.scrolledtext import ScrolledText


def get():
    print(v.get())

master = Tk()
text = ScrolledText(master, font=('微软雅黑'))
# textbar = Scrollbar(master)
# textbar.grid(row=0,column=2)
text = Entry(master, font=('微软雅黑', 20))
text.grid(row=0,column=1, rowspan=4)


MODES = [
    ("Monochrome", "1"),
    ("Grayscale", "L"),
    ("True color", "RGB"),
    ("Color separation", "CMYK"),
]

v = StringVar()
v.set('准备中...')  # initialize
count = 0
for text, mode in MODES:
    b = Radiobutton(master, text=text,
                    variable=v, value=mode)
    # b.pack(anchor=W)

    b.grid(row=count, column=0, sticky=W)
    count += 1

Button(master, text='一键设计签名', font=('微软雅黑', 15), width='15', height='1',
       command=get).grid(row=4, column=1)

# if not v.get():
master.mainloop()


