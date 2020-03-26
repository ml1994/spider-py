import requests
import json
import pickle

username = '15168301541'
password = 'ma199491'
params = {
    'ck': '',
    'name': username,
    'password': password,
    'remember': False,
    'ticket': ''
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
}
res = requests.post('https://accounts.douban.com/j/mobile/login/basic', data=params, headers=headers)
res_json = json.loads(res.text)
if res_json['message'] == 'success':
    print('login success')
    with open('db.cookie', 'wb') as f:
        pickle.dump(res.cookies, f)
else:
    print('login fail')

with open('db.cookie', 'rb') as f:
    cookies = pickle.load(f)
html = requests.get('https://www.douban.com/', cookies=cookies, headers=headers).text
if '早安午安晚安' in html:
    print('already login')
else:
    print('not login')
