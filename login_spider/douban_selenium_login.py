import time

from selenium import webdriver

username = '15168301541'
password = 'ma199491'
url = 'https://www.douban.com'


def login():
    browser = webdriver.Chrome(executable_path='/Users/ml/playground/python-learn/chromedriver')
    browser.get(url)
    # 切到iframe
    browser.switch_to.frame(browser.find_element_by_tag_name('iframe'))
    time.sleep(2)
    btn_psw_login = browser.find_element_by_xpath('//li[@class="account-tab-account"]')
    btn_psw_login.click()

    username_ele = browser.find_element_by_xpath('//input[@id="username"]')
    password_ele = browser.find_element_by_xpath('//input[@id="password"]')
    login_ele = browser.find_element_by_xpath('//div[contains(@class, "account-form-field-submit")]/a')
    username_ele.send_keys(username)
    password_ele.send_keys(password)
    login_ele.click()

    time.sleep(5)
    cookies = {}
    for item in browser.get_cookies():
        cookies[item['name']] = item['value']

    browser.close()
    print(cookies)


if __name__ == '__main__':
    login()