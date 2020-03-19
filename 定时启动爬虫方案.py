"""


"""
import time
import os
# # 1、最简单的定时循环
# while True:
#     os.system("scrapy crawl News")
#     time.sleep(86400)


# 2、使用shced调度（延时处理机制）python自带模块
import sched
# 初始化sched模块，生成调度器对象
# 第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到之前阻塞
schedule = sched.scheduler(time.time, time.sleep)


# 被周期调用触发的函数
def func():
    # os.system("scrapy crawl News")
    print("---开始执行---")
    """
    enter()
    四个参数分别为：
    间隔事件、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数、参数
    """


def perform(inc):
    schedule.enter(inc, 0, perform, (inc,))
    func()


def main():

    schedule.enter(0, 0, perform, (10,))


if __name__ == '__main__':
    main()
    schedule.run()


"""
使用crontab linux命令定时运行爬虫

[分钟] [小时] [每月的某一天] [每年的某一月] [每周的某一天] [执行的命令]

-minute: 区间为 0 – 59

-hour: 区间为0 – 23

-day-of-month: 区间为0 – 31

-month: 区间为1 – 12. 1 是1月. 12是12月.

-Day-of-week: 区间为0 – 7. 周日可以是0或7.
"""


