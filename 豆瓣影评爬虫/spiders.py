

import json
import requests
import pymongo
import random
import csv
import time




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
        self.csv_file = open("dbyp.csv", "a", encoding="utf-8")
        # 初始创建一个csv文件写入对象，可以将数据写入到指定的csv文件中
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_title = False
        self.json_file = open("dbyp.json","a", encoding="utf-8")

    def get_data_from_url(self, url):
        """
        请求url，获取json数据
        """
        print("-"*50)
        print("正在请求的URL：",url)
        response = requests.get(url, headers=self.headers)
        print(response.status_code)
        if response.status_code != 200:
            # 不成功重新放入队列
            self.get_data_from_url(url)
        else:
            return response.json()

    def parse_data(self, datas):
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

        store = []
        # print(datas)
        # print(type(datas))

        res_data = datas
        total = int(res_data['total'])
        interests = res_data['interests']  # 用户评论数据
        print("总评价数量：", total)

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
                store.append(data)
        except Exception as e:
            print("出现异常信息：", e)

        finally:
            print(store[0])
            self.save_to_csv(store)

        return store, total

    def save_to_mongo(self, datas):
        """数据存入mongodb"""
        # 插入多条数据直接使用insert_many 以列表形式，列表的元素必须是字典形式
        print('正在保存{}条数据到mongodb'.format(len(datas)))
        print(datas)
        self.collection.insert_many(datas)

    def __del__(self):
        """当程序结束时关闭数据库链接,文件对象，"""
        self.client.close()
        # 关闭文件对象，将内存缓冲区数据写入磁盘中
        self.csv_file.close()
        self.json_file.close()

    def save_to_csv(self, datas):

        # 表数据
        data_list = [item.values() for item in datas]
        if not self.csv_title:
            # 表头
            table_title = datas[0].keys()
            # 写一行表头数据
            self.csv_writer.writerow(table_title)
            self.csv_title = True

        # 一次性写入多行数据，参数是一个二维嵌套列表,注意有个s
        self.csv_writer.writerows(data_list)
        print("数据已保存到csv文件中")

    def save_to_json(self, datas):
        for data in datas:

            json.dump(data, self.json_file, ensure_ascii=False)
            self.json_file.write("\n")
        print("写入json文件成功")

    def main(self):
        start_time = time.time()
        start = 0
        print("-"*50)
        while True:
            url = self.url.format(start)
            # 发起请求
            json_str = self.get_data_from_url(url)
            # 解析json数据，获取列表信息
            douban_yp, total = self.parse_data(json_str)

            # self.save_to_json(douban_yp)
            self.save_to_mongo(douban_yp)

            start += 25
            print(">>>>>>正在获取第{}页数据".format(start // 25))
            # 如果请求返回的数据不足18条，就可以结束了
            if len(douban_yp) < 20 and start >= total:
                break
            # time.sleep(random.randint(0, 1))
            if start % 1000 == 0:
                print("-------稍微休息一下，友情爬虫------")
                time.sleep(random.randint(1, 5))

        end_time = time.time()
        print("结束，总共耗时：", end_time-start_time)

    def run(self):
        """启动爬虫"""
        # 将任务添加进线程池执行
        pass

if __name__ == '__main__':
    sp = DoubanSpider()
    sp.main()





