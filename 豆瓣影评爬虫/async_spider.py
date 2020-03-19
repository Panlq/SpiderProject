import requests
import csv
import json
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
from lxml import etree
import asyncio
import aiohttp
from http.cookies import SimpleCookie


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36",
}
start_url = "https://movie.douban.com/subject/26752088/comments?start={}&limit=20&sort=new_score"


async def __fetch(url, loop, params=None):
    try:
        async with aiohttp.ClientSession(loop=loop) as session:
            # 发送请求获取页面数据
            async with session.get(url, headers=headers, timeout=5) as response:
                print("正在获取连接:", url)
                assert response.status == 200, "请求失败"
                resp = response.text()               # print(resp)
                return await resp
    except Exception as e:
        # print("__fetch{}:{}".format(url, e))
        print(f"\n###fetch{url}: {e}")


class ParsePage(object):
    def __new__(cls, *args, **kwargs):
            if not hasattr(ParsePage, "__instance"):
                cls.__instance = object.__new__(cls)
            return cls.__instance

    def __init__(self, content):
        self.html = content

    def __enter__(self):
        print("-"*20)
        result = []
        html = etree.HTML(self.html)
        nodes = html.xpath('//div[@class="comment-item"]')
        # print(nodes)
        # print(len(self.html))
        for node in nodes:
            res = {}
            res["name"] = node.xpath('.//span[@class="comment-info"]/a/text()')[0]
            print(res["name"])
            res["votes"] = node.xpath('.//span[@class="votes"]/text()')[0]
            print(res["votes"])
            res["evaluate"] = node.xpath('.//div[@class="comment"]//p/span/text()')[0].strip().encode('gbk', 'ignore').decode('gbk')
            print(res["evaluate"])
            # res["rating"] = node.xpath('.//span[contains(@class, "rating")]/@title')[0]
            res["pub_time"] = node.xpath('.//span[@class="comment-time "]/text()')[0].strip()
            print(res["pub_time"])
            result.append(res)
        try:
            next_page_url = html.xpath('//div[@id="paginator"]/a[@class="next"]/@href')[0]
        except:
            next_page_url = None
        print(next_page_url)
        return result, next_page_url

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


async def getEvaluateInfo(fd, loop):
    for i in range(22):
        try:
            task = asyncio.ensure_future(__fetch(start_url.format(i*20), loop), loop=loop)
            # while True:
            content = await asyncio.wait_for(task, timeout=5)
            print("------%d---------", i+2)
            # print(content)
            with ParsePage(content) as res:
                # 异步存储为csv
                print("*"*30)

                await save_to_json(fd, res[0])
                # return res
        except Exception as e:
            print("error:",e)


async def save_to_json(fd, datas):
    """异步存储为csv文件"""
    for data in datas:
        json.dump(data, fd, ensure_ascii=False)
        fd.write("\n")


if __name__ == '__main__':
    fd = open("dbyp.json", "a")
    loop = asyncio.get_event_loop()

    task = asyncio.ensure_future(getEvaluateInfo(fd, loop), loop=loop)
    loop.run_until_complete(task)
    loop.close()
    fd.close()
