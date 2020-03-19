
# from gevent import monkey
# monkey.patch_all()
# from gevent.pool import Pool
import json
import requests
import pymongo
import random
import csv
import time
from queue import Queue
from multiprocessing.dummy import Pool


total = 200000


class DoubanSpider(object):

    def __init__(self):
        # 需要注意的是要有referer
        self.url = "https://m.douban.com/rexxar/api/v2/movie/26752088/interests?count=20&order_by=hot&start={}&ck=OBxb&for_mobile=1"
        self.headers = {"Referer": "https://m.douban.com/movie/subject/26752088/comments?sort=new_score&start=25",
                        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X)AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
                        "X-Requested-With": "XMLHttpRequest"}
        # 初始化mongodb链接对象
        self.client = pymongo.MongoClient(host="127.0.0.1", port=27017)

        # 链接数据库集合
        self.collection = self.client['douban']['dbyp']

        # 写入csv文件的对象
        self.csv_file = open("dbyp.csv", "w", encoding="utf-8")
        # 初始创建一个csv文件写入对象，可以将数据写入到指定的csv文件中
        self.csv_writer = csv.writer(self.csv_file)

        self.json_file = open("dbyp.json","a", encoding="utf-8")
        self.url_queue = Queue()
        # 响应 队列
        self.page_queue = Queue()
        # 数据 队列
        self.data_queue = Queue()
        # 创建线程池

        self.pool = Pool()

    def add_url_to_queue(self):
        """"""
        start = 0
        while True:
            url = self.url.format(start)
            start += 25
            self.url_queue.put(url)
            print(url)
            # time.sleep(random.randint(0, 0.5))
            if start % 1000 == 0:
                print("-------稍微休息一下，友情爬虫------")
                time.sleep(random.randint(10, 20))
            if start >= 1000:
                break

    def get_data_from_url(self):
        """
        请求url，获取json数据
        """
        print("-"*100)
        while True:
            print(self.url_queue.qsize())
            url = self.url_queue.get()
            # print(url)
            response = requests.get(url, headers=self.headers)
            self.page_queue.put(response.json())

            self.url_queue.task_done()

        # return response.json()

    def parse_data(self):
        """
        解析json数据，获取短评总条数，total
        user_id: 用户id
        user_name:昵称
        create_time:
        conment: 评论
        rating: 推荐指数
        loc_name: 地区  （有些可能是null),做数据分析的话就要做空值处理
        vote_count: 评论点赞数
        uid: 豆瓣账户id
        """
        print("+"*100)
        global total
        store = []
        while True:
            # datas = self.data_queue.get()

            # print(datas)
            # print(type(datas))
            res_data = self.data_queue.get()
            total = int(res_data['total'])
            interests = res_data['interests']  # 用户评论数据
            print("总评价数量：", total)

            # 循环结束条件
            if len(interests) < 20:
                break
            # 有些数据是null 所以取不到会报错，为了避免停止程序运行做异常捕获
            try:
                for item in interests:
                    data = {}
                    data["comment"] = item["comment"]
                    data["create_time"] = item["create_time"]
                    data["user_id"] = item["user"]["id"]
                    data["user_name"] = item["user"]["name"]

                    if item["user"]["loc"]:
                        data["loc"] = item["user"]["loc"]
                    else:
                        data["loc_name"] = "None"
                    data["uid"] = item["user"]["uid"]
                    data["vote_count"] = item.get("vote_count", "None")
                    # print(data)
                    store.append(data)
            except Exception as e:
                print("出现异常信息：", e)

            finally:
                self.save_to_csv(store)
                self.data_queue.put(store)
                self.page_queue.task_done()

        # return store, total

    def save_to_mongo(self):
        """数据存入mongodb"""
        print("&" * 100)
        while True:
            datas = self.data_queue.get()
            # 插入多条数据直接使用insert_many 以列表形式，列表的元素必须是字典形式
            print('正在保存数据到mongodb')
            self.collection.insert_many(datas)
            self.data_queue.task_done()

    def __del__(self):
        """当程序结束时关闭数据库链接,文件对象，"""
        self.client.close()
        # 关闭文件对象，将内存缓冲区数据写入磁盘中
        self.csv_file.close()
        self.json_file.close()

    def save_to_csv(self, datas):
        # 表头
        table_title = datas[0].keys()
        # 表数据
        data_list = [list(item.values()) for item in datas]

        # 写一行表头数据
        self.csv_writer.writerow(table_title)
        # 一次性写入多行数据，参数是一个二维嵌套列表
        self.csv_writer.writerow(data_list)
        print("数据已保存到csv文件中")

    def save_to_json(self, datas):
        for data in datas:

            json.dump(data, self.json_file, ensure_ascii=False)
            self.json_file.write("\n")
        print("写入json文件成功")

    def run_use_more_task(self, func, count=1):
        """把func放到线程中执行，将任务加入线程池"""
        for i in range(0, count):
            # 使用线程池执行任务
            self.pool.apply_async(func)

    def run(self):
        """启动爬虫"""
        # 将任务添加进线程池执行
        self.run_use_more_task(self.add_url_to_queue)
        time.sleep(2)
        self.run_use_more_task(self.get_data_from_url, 5)
        time.sleep(2)
        self.run_use_more_task(self.parse_data, 2)

        print("队列长度：", self.data_queue.qsize())
        time.sleep(1)
        self.run_use_more_task(self.save_to_mongo, 1)

        # 由于异步执行，主线程加载完后，子线程还没准备好后就结束了，所以要加一个延时
        time.sleep(0.1)

        # 使用队列join方法，等待队列任务都完成了才结束

        self.url_queue.join()
        self.page_queue.join()
        self.data_queue.join()


if __name__ == '__main__':
    sp = DoubanSpider()
    sp.run()





