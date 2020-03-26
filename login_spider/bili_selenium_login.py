import time
import random
from io import BytesIO

from selenium import webdriver
from PIL import Image
from selenium.webdriver import ActionChains

username = '15168301541'
password = 'ma199491'
url = 'https://passport.bilibili.com/login'

browser = webdriver.Chrome(executable_path='/Users/ml/playground/python-learn/chromedriver')
browser.get(url)
browser.maximize_window()  # 重要！放大窗口好定位


def login():
    username_ele = browser.find_element_by_xpath('//input[@id="login-username"]')
    password_ele = browser.find_element_by_xpath('//input[@id="login-passwd"]')
    login_ele = browser.find_element_by_xpath('//a[@class="btn btn-login"]')
    username_ele.send_keys(username)
    password_ele.send_keys(password)
    login_ele.click()
    time.sleep(1)
    image = crop_image('image.png')

    show_full_img_script = "document.querySelector('.geetest_canvas_fullbg').style = 'block'"
    browser.execute_script(show_full_img_script)
    image_full = crop_image('image_full.png')

    # 初始left值，避开左边的不同像素，寻找缺口
    init_left = 60
    img_width = image.size[0]
    img_height = image.size[1]
    print('img_width={}'.format(img_width))
    print('img_height={}'.format(img_height))
    has_find = False
    diff_left = 0
    # mac 两倍像素
    for i in range(img_width - 1, init_left * 2, -1):
        if has_find:
            break
        for j in range(img_height):
            if not compare_pixel(image, image_full, i, j):
                diff_left = i
                print(i)
                has_find = True
                break
    # 应拖动距离
    diff_left = diff_left - 100
    print('diff_left={}'.format(diff_left))

    # 拖动
    drop_btn = browser.find_element_by_xpath('//div[@class="geetest_slider_button"]')
    ActionChains(browser).click_and_hold(drop_btn).perform()
    # 拖动距离是物理像素
    drop_list = drop_track(diff_left / 2)
    for offset in drop_list:
        # 拖动卡顿 selenium/webdriver/common/actions/pointer_input 中修改DEFAULT_MOVE_DURATION值，默认为250
        ActionChains(browser).move_by_offset(xoffset=offset, yoffset=0).perform()
    time.sleep(0.5)
    ActionChains(browser).release().perform()
    try:
        success_ele = browser.find_element_by_xpath('//div[@class="geetest_panel_success"]')
    except Exception as e:
        # 没成功
        retry_ele = browser.find_element_by_xpath('//div[@class="geetest_panel_error_content"]')
        retry_ele.click()
        login()


def crop_image(name):
    time.sleep(2)
    img = browser.find_element_by_xpath('//div[@class="geetest_window"]')
    size = img.size
    location = img.location
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    buttom = location['y'] + size['height']
    box = (int(left), int(top), int(right), int(buttom))

    screenshot = browser.get_screenshot_as_png()
    screenshot = Image.open(BytesIO(screenshot))
    # mac下像素要乘2？
    box = map(lambda x: x * 2, box)
    captcha = screenshot.crop(box)
    captcha.save(name)
    return captcha


def compare_pixel(img, img_full, i, j):
    pixel1 = img.load()[i, j]
    pixel2 = img_full.load()[i, j]
    # 像素容错差
    threshold = 60

    if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(pixel1[2] - pixel2[2]) < threshold:
        return True
    return False


def drop_track(offset):
    track = []
    final_left = offset
    now_left = 0
    mid = offset * 3 / 4
    v = 0
    t = 0.1
    while now_left < final_left:
        if now_left < mid:
            a = random.randint(8, 9)
        else:
            a = -random.randint(6, 7)
        v0 = v
        v = v0 + a*t
        move = v0*t + 1/2*a*t*t
        now_left += move
        track.append(round(move))
    return track


if __name__ == '__main__':
    login()

