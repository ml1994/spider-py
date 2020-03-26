import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy import Selector

# headless
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
# 不加载图片
chrome_options.add_argument('blink-settings=imagesEnabled=false')

browser = webdriver.Chrome(executable_path='/Users/ml/playground/python-learn/chromedriver', chrome_options=chrome_options)


def parse_detail(url):
    browser.get(url)
    time.sleep(1)
    sel = Selector(text=browser.page_source)
    sku_name = sel.xpath('//div[@class="sku-name"]/text()').extract()[0].strip()
    sku_price = float(sel.xpath('//div[@class="summary-price J-summary-price"]//span[contains(@class, "J-p-")]/text()').extract()[0])
    pass

if __name__ == '__main__':
    url = 'https://item.jd.com/100009414592.html'
    parse_detail(url)