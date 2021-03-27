# -*- coding: UTF-8 -*-
import user_agents
import requests
import yaml
import os
import time as TIME
from datetime import datetime
from datetime import timedelta
from http.server import BaseHTTPRequestHandler
from urllib import parse

# 增加叨叨 -------------------start
def creat_data(time, user_info, data, since):
    text=''
    judegement = judge_time_excit(github_daodao_config(user_info, since), time)
    if (judegement['flag']):
        text = 'Execution: Today has sent daodao, find issue, add comment!'
        creat_a_new_comments(user_info, judegement['last_issue_number'], data)
    else:
        text = 'Execution: You did not send a message today, create an issue and add a comment!'
        creat_a_new_day_issue(user_info, time)
        judegement = judge_time_excit(github_daodao_config(user_info, since), time)
        creat_a_new_comments(user_info, judegement['last_issue_number'], data)
	@@ -71,16 +71,16 @@ def delete_data_muti(number, search_time_limit, search_time_limit_num, zone):
    text=''
    handle_number = 0
    list = search_daodao(search_time_limit, search_time_limit_num, zone)
    if len(list) > int(number):
        handle_number = number
    else:
        handle_number = len(list)
    if handle_number > 0:
        for i in list[0:handle_number]:
            delete_data(i['id'])
        text= 'Execution: Deleted latest'+handle_number+'daodao!'
    else:
        text="Execution: You don't have a word to say!"
    return text


	@@ -167,7 +167,7 @@ def judge_time_excit(list, time):
    flag = False
    last_issue_number = 0
    for i in list:
        if int(i['number']) > int(last_issue_number):
            last_issue_number = i['number']
        if i['title'] == str(time):
            flag = True
	@@ -234,24 +234,24 @@ def return_time(i):

class handler(BaseHTTPRequestHandler):
    def do_GET(self):

    # 传入数据
        config = load_yaml_config('/config.yml')['setting']
    # 默认测试数据
        data = config['data']
    # 时区
        zone = config['zone']
    # 查询天数
        search_time_limit = config['search_time_limit']
    # 查询条数
        search_time_limit_num = config['search_time_limit_num']
    # 生成标准时间
        now = datetime.utcnow()
    # 读取用户信息
        user_info = {
        "token": os.environ["DAODAO_TOKEN"],
        "user": config['user'],
        "source": config['repo']
        }
    # 生成当前时区时间标题
        now_time = time_zone_reset(now, zone, '%Y-%m-%d')
	@@ -260,19 +260,19 @@ def do_GET(self):

        print('当地时间为：', now_time)

        o = parse.urlparse(self.path)
        if 'creat' in parse.parse_qs(o.query):
            data = parse.parse_qs(o.query)['creat'][0]
            text = creat_data(now_time, user_info,'{"content":'+ data+',\n"user_agents":"'+'"}', since)
        elif 'delete' in parse.parse_qs(o.query):
            num = parse.parse_qs(o.query)['delete'][0]
            text = delete_data_muti(num,search_time_limit, search_time_limit_num, zone)
        else:
            text = 'please check!'

        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('charset','UTF-8')
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(text.encode())
