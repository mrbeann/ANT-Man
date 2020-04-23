import json
import requests
import time
import random
import os
from flask import Flask
from threading import Thread

ip = None
s_ip = Nones
path = None


def compose_post(reqs_per_sec):
    num_threads = 4
    num_conns = 10
    duration = 30
    cmd = 'cd {} && ./wrk -D exp -t {} -c {} -d {} -L -s ' \
          './scripts/social-network/compose-post.lua http://{}:8080/wrk2-api/post/compose -R {}'.format(
          path, num_threads, num_conns, duration, ip, reqs_per_sec)
    p = os.popen(cmd)
    print('compose_post visit done')
    x=p.readlines()
    for line in x:
        print('ssss='+line)


def home_timeline(reqs_per_sec):
    num_threads = 4
    num_conns = 10
    duration = 30
    cmd = 'cd {} && ./wrk -D exp -t {} -c {} -d {} -L -s ' \
          './scripts/social-network/read-home-timeline.lua http://{}:8080/wrk2-api/home-timeline/read -R {}'.format(
        path,num_threads, num_conns, duration, ip, reqs_per_sec)
    p = os.popen(cmd)
    print('home_timeline visit done')


def user_timeline(reqs_per_sec):
    num_threads = 4
    num_conns = 10
    duration = 30
    cmd = 'cd {} && ./wrk -D exp -t {} -c {} -d {} -L -s ' \
          './scripts/social-network/read-user-timeline.lua http://{}:8080/wrk2-api/user-timeline/read -R {}'.format(
        path, num_threads, num_conns, duration, ip, reqs_per_sec)
    p = os.popen(cmd)
    print('user_timeline visit done')


def ratio_many_user(workers):
    basic, advance = int(workers.split('v')[0]), int(workers.split('v')[1])
    if basic == 0:
        compose_post(advance)
    else:
        home_timeline(basic)


app = Flask(__name__)


@app.route('/composepost/<int:post_id>')
def bshow_post(post_id):
    # show the post with the given id, the id is an integer
    from threading import Thread
    thread = Thread(target=compose_post, kwargs={'reqs_per_sec': post_id})
    thread.start()
    return 'Workers %d' % post_id


@app.route('/hometimeline/<int:post_id>')
def ashow_post(post_id):
    # show the post with the given id, the id is an integer
    from threading import Thread
    thread = Thread(target=home_timeline, kwargs={'reqs_per_sec': post_id})
    thread.start()
    return 'Workers %d' % post_id


@app.route('/usertimeline/<int:post_id>')
def mshow_post(post_id):
    # show the post with the given id, the id is an integer

    thread = Thread(target=user_timeline, kwargs={'reqs_per_sec': post_id})
    thread.start()
    return 'Workers %d' % post_id


@app.route('/ratioworkers/<post_id>')
def rshow_post(post_id):
    thread = Thread(target=ratio_many_user, kwargs={'workers': post_id})
    thread.start()
    return 'Workers %s' % post_id


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host=s_ip, port='9082')
