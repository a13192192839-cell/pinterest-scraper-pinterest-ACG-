import time
import requests
import os
from urllib.parse import urlparse
import json
import base64
import random

os.makedirs('C:/my_images_pinterest/my_images_a', exist_ok=True)
os.makedirs('C:/my_images_pinterest/The_pin', exist_ok=True)
f_path = 'C:/my_images_pinterest/The_pin/old_pin.txt'
if not os.path.exists(f_path):
    with open(f_path, 'a') as old_pin_f:
        pass


def request_json(request_params, max_retries=3, base_delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            resp = session.get(url, headers=headers, params=request_params, timeout=10)
            resp.raise_for_status()  # 4xx/5xx 也当失败处理
            return resp.json()
        except Exception as e:
            print(f'请求失败(第{attempt}/{max_retries}次):{e}')
            if attempt == max_retries:
                return None
            time.sleep(base_delay * attempt)


def read_pin():
    pin_file_path = r"C:\my_images_pinterest\The_pin\old_pin.txt"
    with open(pin_file_path, "r", encoding="utf-8") as f:
        raw_content = f.read()
    raw_content = raw_content.split("\n")
    return raw_content, pin_file_path


def random_(a, b):
    function_interval = random.uniform(a, b)
    return function_interval


def decoded_base64(function_decoded):
    function_real_pin_id = function_decoded.split(':')[1]  # "955255771125502846"
    new_pin_ids.append(function_real_pin_id)
    return function_real_pin_id


def dow_photo(function_img):
    with open(save_path, 'wb') as f:
        f.write(function_img)
        time.sleep(interval)
        print(f'{filename}{p}下载完成')
        seen.add(filename)
        return True


def new_pin_ids_pop():
    function_next_pin = None
    while new_pin_ids:
        candidate = new_pin_ids.pop(0)  # 先拿第一个试试
        if candidate not in old_pin_ids:
            function_next_pin = candidate
            break
    return function_next_pin


url = 'https://jp.pinterest.com/resource/RelatedModulesResource/get/'

headers = {'user-agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/151.0.0.0 Safari/537.36',
           'referer': 'https://jp.pinterest.com/',
           'x-requested-with': 'XMLHttpRequest',
           'x-pinterest-pws-handler': 'www/pin/[id].js',
           'x-pinterest-appstate': 'active',
           'x-app-version': '30c1eaf',
           'accept': 'application/json, text/javascript, */*, q=0.01',
           'x-pinterest-source-url':
               '/pin/103582860175535578/'
           }
session = requests.Session()

starting_pin_id = '910853093405495373'  # 抓取起点

data = {"options": {"additional_fields": ["pin.gen_ai_topics"], "pin_id": f"{starting_pin_id}", "context_pin_ids": [],
                    "context_near_dup_image_sigs": [], "homefeed_source_sig": None, "page_size": 12,
                    "search_query": "人物艺术", "source": "search", "top_level_source": "search",
                    "top_level_source_depth": 1, "is_pdp": False,
                    "client_tracking_params": "CwABAAAAEDg3OTA4MjYyNzQ2MTg1OTcLAAcAAAAPdW5rbm93bi91bmtub3duAA"},
        "context": {}}

data_json_string = json.dumps(data, ensure_ascii=False)
params = {
    'source_url': f'/pin/{starting_pin_id}/',
    'data': data_json_string,  # key 要用接口认识的 'data',值是你算出来的那个字符串
    '_': str(int(time.time() * 1000))
}

list_response = request_json(params)
if list_response is None:
    print('初始化失败，退出')
    raise SystemExit(1)

r = list_response["resource_response"]['data']

p = 0

content, folder = read_pin()

seen = set(os.listdir('C:/my_images_pinterest/my_images_a/'))
new_pin_ids = []  # 收集这一批解出来的 pin_id,供下一轮使用
old_pin_ids = set(content)

while p <= 3:

    interval = random_(1, 1.5)
    for i in r:
        node_id_raw = i.get('node_id')
        if 'images' in i:
            if node_id_raw:
                try:
                    decoded = base64.b64decode(node_id_raw).decode()  # "Pin:955255771125502846"
                    real_pin_id = decoded_base64(decoded)
                except Exception as e:
                    print(e)
            else:
                real_pin_id = None

            i_url = i['images']['orig']["url"]
            # urlparse(i_url).path 会取出 /originals/00/4a/03/004a031b8eb6f5a852904c9685994d44.jpg，
            # 再用 os.path.basename() 只保留最后的文件名 004a031b8eb6f5a852904c9685994d44.jpg，这样存下来的就是合法路径了。
            filename = os.path.basename(urlparse(i_url).path)
            try:
                if filename in seen:
                    continue
                else:
                    img = session.get(i_url, headers=headers).content
                    save_path = os.path.join('C:/my_images_pinterest/my_images_a/', filename)
                    if dow_photo(img):
                        p += 1
            except Exception as e:
                print(f'{filename}{p}下载失败，{e}')

    next_pin = new_pin_ids_pop()
    if next_pin is None:
        break

    # 切换新pin
    old_pin_ids.add(next_pin)
    with open(folder, 'a', encoding="utf-8") as f:
        f.write(str(next_pin).strip() + '\n')
    data["options"]["pin_id"] = next_pin  # 换成新的中心点
    print("换成新的中心点:", next_pin)

    try:
        data_json_string = json.dumps(data, ensure_ascii=False)
        params["data"] = data_json_string
        params["source_url"] = f"/pin/{next_pin}/"
        params["_"] = str(int(time.time() * 1000))
    except Exception as e:
        print(f'错误:{e},跳过')

    r_j = request_json(params)
    if r_j is None:
        print('请求失败，跳过')
    else:
        r = r_j["resource_response"]['data']

    time.sleep(interval)

print('over')
