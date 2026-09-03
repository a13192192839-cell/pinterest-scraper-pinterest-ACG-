import time
import requests
import os
from urllib.parse import urlparse
import json
import base64
import random

os.makedirs('my_images_a', exist_ok=True)
url = 'https://jp.pinterest.com/resource/RelatedModulesResource/get/'

headers = {'user-agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/151.0.0.0 Safari/537.36',
           'referer': 'https://jp.pinterest.com/',
           'Cookie': 'YOUR_COOKIE_HERE',
           'x-requested-with': 'XMLHttpRequest',
           'x-pinterest-pws-handler': 'www/pin/[id].js',
           'x-pinterest-appstate': 'active',
           'x-app-version': '30c1eaf',
           'accept': 'application/json, text/javascript, */*, q=0.01',
           'x-pinterest-source-url':
               ''
           }

starting_pin_id = '103582860175535578'  # 抓取起点

data = {"options": {"additional_fields": ["pin.gen_ai_topics"], "pin_id": f"{starting_pin_id}", "context_pin_ids": [],
                    "context_near_dup_image_sigs": [], "homefeed_source_sig": None, "page_size": 12,
                    "search_query": "人物艺术", "source": "search", "top_level_source": "search",
                    "top_level_source_depth": 1, "is_pdp": False,
                    "client_tracking_params": ""},
        "context": {}}
data_json_string = json.dumps(data, ensure_ascii=False)
params = {
    'source_url': f'/pin/{starting_pin_id}/',
    'data': data_json_string,  # key 要用接口认识的 'data',值是你算出来的那个字符串
    '_': str(int(time.time() * 1000))
}

response = requests.get(url, headers=headers, params=params)
print("状态码:", response.status_code)
list_response = response.json()

# objects and items is 8
r = list_response["resource_response"]['data']

p = 0
seen = set()
new_pin_ids = []  # 收集这一批解出来的 pin_id ,供下一轮使用
old_pin_ids = []  # 收集已经出现过的pin_id ,用来隔离

while p <= 100:

    interval = random.uniform(1, 1.5)
    for i in r:
        node_id_raw = i.get('node_id')
        if 'images' in i:
            if node_id_raw:
                decoded = base64.b64decode(node_id_raw).decode()  # "Pin:955255771125502846"
                real_pin_id = decoded.split(':')[1]  # "955255771125502846"
                new_pin_ids.append(real_pin_id)
            else:
                real_pin_id = None

            i_url = i['images']['orig']["url"]

            try:
                if i_url in seen:
                    continue
                else:
                    img = requests.get(i_url, headers=headers).content
                    # urlparse(i_url).path 会取出 /originals/00/4a/03/004a031b8eb6f5a852904c9685994d44.jpg，
                    # 再用 os.path.basename() 只保留最后的文件名 004a031b8eb6f5a852904c9685994d44.jpg，这样存下来的就是合法路径了。
                    filename = os.path.basename(urlparse(i_url).path)
                    save_path = os.path.join('./my_images_a/', filename)
                    with open(save_path, 'wb') as f:
                        f.write(img)
                        time.sleep(interval)
                        p += 1
                        print(f'{i_url}{p}下载完成')
                        seen.add(i_url)

            except Exception as e:
                print(f'{i_url}{p}下载失败，{e}')
    next_pin = None
    while new_pin_ids:  # 确保每次都是新pin
        candidate = new_pin_ids.pop(0)  # 先拿第一个试试
        if candidate not in old_pin_ids:
            next_pin = candidate
            break
    if next_pin is None:
        break
    old_pin_ids.append(next_pin)
    data["options"]["pin_id"] = next_pin  # 换成新的中心点
    print("换成新的中心点:", next_pin)
    data_json_string = json.dumps(data, ensure_ascii=False)
    params["data"] = data_json_string
    params["source_url"] = f"/pin/{next_pin}/"
    params["_"] = str(int(time.time() * 1000))
    response2 = requests.get(url, headers=headers, params=params)
    r_j = response2.json()
    r = r_j["resource_response"]['data']

    time.sleep(interval)

print('over')
