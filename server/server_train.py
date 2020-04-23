import json
import requests
import time
import random
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from flask import Flask
from threading import Thread

"""
request generator for trainticket
"""
ip = None
s_ip = None
departure_time = "2020-04-15"


# advanced search
def advanced_visit(sleep_list):
    # print('advanced')
    data = {"startingPlace": "Nan Jing",
            "endPlace": "Shang Hai",
            "departureTime": departure_time}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/71.0.3578.98 Safari/537.36',
        'Host': ip + ":80",
        'Accept-Language': "zh-CN,zh;q=0.9",
        'Accept-Encoding': "gzip, deflate",
        'Content-Type': "application/json",
        'Connection': "keep-alive",
        'Referer': "http://"+ip+":80/client_adsearch.html",
        }

    # print('in visit ', time.time())
    for i in sleep_list:
        response = requests.post('http://'+ip+':80/travelPlan/getCheapest', data=json.dumps(data),
                                 headers=headers, timeout=80)
        time.sleep(i)
    print(response, time.time())
    return 0


def advanced_many_user(workers):
    sleep_list = [0] * 15
    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(advanced_visit, [sleep_list for i in range(30)])


def basic_visit(sleep_list):
    # print('basic')
    data = {"startingPlace": "Nan Jing",
            "endPlace": "Shang Hai",
            "departureTime": departure_time}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/71.0.3578.98 Safari/537.36',
        'Host': ip+":80",
        'Accept-Language': "zh-CN,zh;q=0.9",
        'Accept-Encoding': "gzip, deflate",
        'Content-Type': "application/json",
        'Connection': "keep-alive",
        'Referer': "http://"+ip+"/index.html",
    }

    for i in sleep_list:
        # print('in visit ', time.localtime(time.time()))
        response = requests.post('http://'+ip+':80/travel/query', data=json.dumps(data), headers=headers,
                                 timeout=60)
        time.sleep(i)
    print(response)
    return 0


def basic_many_user(workers):
    sleep_list = [0.1] * 10
    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(basic_visit, [sleep_list for i in range(30)])


def mixed_many_user(workers):
    sleep_list = [0.1] * 10
    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(basic_visit, [sleep_list for i in range(30)])
        executor.map(advanced_visit, [sleep_list for i in range(30)])


def ratio_many_user(workers):
    sleep_list = [0.1] * 5
    basic, advance = int(workers.split('v')[0]), int(workers.split('v')[1])
    with ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(basic_visit, [sleep_list for _ in range(basic//3)])
        executor.map(advanced_visit, [sleep_list for _ in range(advance//3)])
        executor.map(basic_visit, [sleep_list for _ in range(basic//3)])
        executor.map(advanced_visit, [sleep_list for _ in range(advance//3)])
        executor.map(basic_visit, [sleep_list for _ in range(basic//3)])
        executor.map(advanced_visit, [sleep_list for _ in range(advance//3)])


app = Flask(__name__)


@app.route('/basicworkers/<int:post_id>')
def bshow_post(post_id):
    # show the post with the given id, the id is an integer
    thread = Thread(target=advanced_many_user, kwargs={'workers': post_id})
    thread.start()
    return 'Workers %d' % post_id


@app.route('/advancedworkers/<int:post_id>')
def ashow_post(post_id):
    # show the post with the given id, the id is an integer
    thread = Thread(target=advanced_many_user, kwargs={'workers': post_id})
    thread.start()
    return 'Workers %d' % post_id


@app.route('/mixeddworkers/<int:post_id>')
def mshow_post(post_id):
    # show the post with the given id, the id is an integer
    thread = Thread(target=mixed_many_user, kwargs={'workers': post_id})
    thread.start()
    return 'Workers %d' % post_id


@app.route('/ratioworkers/<post_id>')
def rshow_post(post_id):
    # show the post with the given id, the id is an integer
    thread = Thread(target=ratio_many_user, kwargs={'workers': post_id})
    thread.start()
    return 'Workers %s' % post_id


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host=s_ip, port='9081')
