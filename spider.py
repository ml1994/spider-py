import ast
import re
from datetime import datetime
from urllib import parse

import requests
from scrapy import Selector

from csdn_spider.models import *


domain = 'https://bbs.csdn.net'
def get_nodes_json():
    left_menu_text = requests.get('https://bbs.csdn.net/dynamic_js/left_menu.js?csdn').text
    node_str_match = re.search('forumNodes: (.*])', left_menu_text)
    if node_str_match:
        node_str = node_str_match.group(1).replace('null', 'None')
        node_list = ast.literal_eval(node_str)
        return node_list
    return []

# 递归的变量放外面不容易出错
last_url_list = []
def get_last_url_list(nodes_list):
    for item in nodes_list:
        if 'children' in item and item['children']:
            get_last_url_list(item['children'])
        else:
            if 'url' in item and item['url']:
                last_url_list.append(item['url'])

def get_all_url_list(last_list):
    all_url = []
    for url in last_list:
        all_url.append(parse.urljoin(domain, url))
        all_url.append(parse.urljoin(domain, url + '/recommend'))
        all_url.append(parse.urljoin(domain, url + '/closed'))

    return all_url


def parse_list(url):
    res_text = requests.get(url).text
    sel = Selector(text=res_text)
    all_trs = sel.xpath('//table[@class="forums_tab_table"]/tbody/tr')
    for tr in all_trs:
        status = tr.xpath('.//td[1]/span/text()').extract()[0]
        score = tr.xpath('.//td[2]/em/text()').extract()[0]
        topic_url = parse.urljoin(domain, tr.xpath('.//td[3]/a[contains(@class,"forums_title")]/@href').extract()[0])
        topic_title = tr.xpath('.//td[3]/a[contains(@class,"forums_title")]/text()').extract()[0]
        author_url = parse.urljoin(domain, tr.xpath('.//td[4]/a/@href').extract()[0])
        author_id = author_url.split('/')[-1]
        create_time_str = tr.xpath('.//td[4]/em/text()').extract()[0]
        create_time = datetime.strptime(create_time_str, '%Y-%m-%d %H:%M')
        answer_info = tr.xpath('.//td[5]/span/text()').extract()[0]
        answer_nums = answer_info.split('/')[0]
        click_nums = answer_info.split('/')[1]
        last_time_str = tr.xpath('.//td[6]/em/text()').extract()[0]
        last_time = datetime.strptime(last_time_str, '%Y-%m-%d %H:%M')

        topic = Topic()
        topic.status = status
        topic.score = int(score)
        topic.id = int(topic_url.split('/')[-1])
        topic.title = topic_title
        topic.author = author_id
        topic.click_nums = int(click_nums)
        topic.answer_nums = int(answer_nums)
        topic.create_time = create_time
        topic.last_time = last_time

        # 如果设置了自己的id，save认为这是更新操作，本身没有这个值，所以无法添加数据
        existed_topics = Topic.select().where(Topic.id == topic.id)
        if existed_topics:
            topic.save()
        else:
            topic.save(force_insert=True)

        # parse_topic(topic_url)
        # parse_author(author_url)

    # 分页 上一页和下一页用的相同class 需要处理
    page_num = 1
    url_match = re.search('\?page=(\d+)', url)
    if url_match:
        page_num = int(url_match.group(1))
    next_page = sel.xpath('//a[@class="pageliststy next_page"]/@href').extract()
    if next_page:
        page_url_match = re.search('\?page=(\d+)', next_page[-1])
        if page_url_match:
            if int(page_url_match.group(1)) > page_num:
                next_url = parse.urljoin(domain, next_page[-1])
                parse_list(next_url)


def parse_topic(url):
    # 获取帖子详情
    res_text = requests.get(url).text
    sel = Selector(text=res_text)
    all_divs = sel.xpath('//div[starts-with(@id, "post-")]')
    answer_list = all_divs

    page_num = 1
    url_match = re.search('(\d+)\?page=(\d+)', url)
    topic_id = ''
    if url_match:
        topic_id = url_match.group(1)
        page_num = int(url_match.group(2))
    else:
        # 第一页
        topic_id = url.split('/')[-1]
        answer_list = all_divs[1:]

        topic_item = all_divs[0]
        content = topic_item.xpath('.//div[@class="post_body post_body_min_h"]').extract()[0]
        praised_nums = topic_item.xpath('.//label[@class="red_praise digg"]/em/text()').extract()[0]
        jtl_str = topic_item.xpath('.//div[@class="close_topic"]/text()').extract()[0]
        jtl_match = re.search('(\d+\.?\d*)%', jtl_str)
        jtl = 0
        if jtl_match:
            jtl = jtl_match.group(1)

        # 更新topic表数据
        existed_topic = Topic.select().where(Topic.id == topic_id)
        if existed_topic:
            topic = existed_topic[0]
            topic.content = content
            topic.praised_nums = int(praised_nums)
            topic.jtl = float(jtl)

            topic.save()

    for answer_item in answer_list:
        answer = Answer()
        answer_author = answer_item.xpath('.//div[@class="nick_name"]/a/text()').extract()[0]
        answer_content = answer_item.xpath('.//div[@class="post_body post_body_min_h"]').extract()[0]
        answer_create_time_str = answer_item.xpath('.//label[@class="date_time"]/text()').extract()[0]
        answer_create_time = datetime.strptime(answer_create_time_str, '%Y-%m-%d %H:%M:%S')
        answer_praised_nums = answer_item.xpath('.//label[@class="red_praise digg"]/em/text()').extract()[0]

        answer.topic_id = int(topic_id)
        answer.author = answer_author
        answer.content = answer_content
        answer.create_time = answer_create_time
        answer.praised_nums = int(answer_praised_nums)

        answer.save()

    # 分页 上一页和下一页用的相同class 需要处理
    next_page = sel.xpath('//a[@class="pageliststy next_page"]/@href').extract()
    if next_page:
        page_url_match = re.search('\?page=(\d+)', next_page[-1])
        if page_url_match:
            if int(page_url_match.group(1)) > page_num:
                next_url = parse.urljoin(domain, next_page[-1])
                parse_topic(next_url)

def parse_author(url):
    # 获取用户详情
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }
    res_text = requests.get(url, headers=headers).text
    sel = Selector(text=res_text)


if __name__ == '__main__':
    get_last_url_list(get_nodes_json())
    all_list = get_all_url_list(last_url_list)
    for url in all_list[:2]:
        parse_list(url)
