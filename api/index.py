# -*- coding: UTF-8 -*-
import requests
import yaml
import os
import time as TIME
from datetime import datetime
from datetime import timedelta
from http.server import BaseHTTPRequestHandler
from urllib import parse
import user_agents
import json

# 增加叨叨 -------------------start
def creat_data(time, user_info, data, since):
    text=''
    judegement = judge_time_excit(github_daodao_config(user_info, since), time)
    if (judegement['flag']):
        text = 'Execution: today has sent daodao, find issue, add comment!'
        creat_a_new_comments(user_info, judegement['last_issue_number'], data)
    else:
        text = 'Execution: you did not send a message today, create an issue and add a comment!'
        creat_a_new_day_issue(user_info, time)
        judegement = judge_time_excit(github_daodao_config(user_info, since), time)
        creat_a_new_comments(user_info, judegement['last_issue_number'], data)
    return text

# 增加叨叨 -生成一个新叨叨
def creat_a_new_comments(user_info, number, body):
    requests_path = 'https://api.github.com/repos/' + user_info['user'] + '/' + user_info['source'] + '/issues/' + str(
        number) + '/comments'
    token = 'token ' + user_info['token']
    r = requests.post(requests_path,
                      json={"body": body},
                      headers={"User-Agent": 'curl/7.52.1',
                               'Content-Type': 'application/json',
                               'Accept': 'application/vnd.github.everest-preview+json',
                               'Authorization': token})
    return print('新建评论响应:', r.status_code)


# 增加叨叨 -生成一个新日期
def creat_a_new_day_issue(user_info, time):
    requests_path = 'https://api.github.com/repos/' + user_info['user'] + '/' + user_info['source'] + '/issues'
    token = 'token ' + user_info['token']
    r = requests.post(requests_path,
                      json={"title": time,
                            "body": '叨叨提醒您，今天是：' + time},
                      headers={"User-Agent": 'curl/7.52.1',
                               'Content-Type': 'application/json',
                               'Accept': 'application/vnd.github.everest-preview+json',
                               'Authorization': token})
    return print('新建issue响应:', r.status_code)


# -------------------end

# 删除叨叨 -------------------start
# 基础封装
def delete_data(user_info,data_id):
    requests_path = 'https://api.github.com/repos/' + user_info['user'] + '/' + user_info[
        'source'] + '/issues/comments/' + str(data_id)
    token = 'token ' + user_info['token']
    r = requests.delete(requests_path,
                        headers={"User-Agent": 'curl/7.52.1',
                                 'Content-Type': 'application/json',
                                 'Accept': 'application/vnd.github.everest-preview+json',
                                 'Authorization': token})
    return print('删除响应:', r.status_code)


# 循环列表封装
def delete_data_muti(number,user_info,  search_time_limit, search_time_limit_num):
    number =int(number)
    text=''
    handle_number = 0
    list = search_daodao(user_info, search_time_limit, search_time_limit_num)
    if int(len(list)) > int(number):
        handle_number = number
    else:
        handle_number =  int(len(list))
    if int(handle_number) > 0:
        for i in list[0:int(handle_number)]:
            delete_data(user_info,i['id'])
        text= 'Execution: deleted latest '+str(handle_number)+' daodao!'
    else:
        text='Execution: there is no daodao!'
    return text

# 单一封装
def delete_data_single(number,user_info,  search_time_limit, search_time_limit_num):
    number =int(number)
    text=''
    list = search_daodao(user_info, search_time_limit, search_time_limit_num)
    if int(len(list)) >= int(number) and number > 0:
        delete_data(user_info,list[number-1]['id'])
        text= 'Execution: deleted No.'+str(number)+' daodao!'
    else:
        text='please check!out of range!'
    return text

# -------------------end

# 改动叨叨 -------------------start
# 基础封装
def change_data(user_info,data_id, data):
    requests_path = 'https://api.github.com/repos/' + user_info['user'] + '/' + user_info[
        'source'] + '/issues/comments/' + str(data_id)
    token = 'token ' + user_info['token']
    r = requests.patch(requests_path,
                       json={"body": data},
                       headers={"User-Agent": 'curl/7.52.1',
                                'Content-Type': 'application/json',
                                'Accept': 'application/vnd.github.everest-preview+json',
                                'Authorization': token})
    return print('更改响应:', r.status_code)


# 类型封装
# append 加字符串
# edit 修改字符串
# combine 结合字符串
def change_data_handle(number, data, type, search_time_limit, search_time_limit_num, zone, now_time, user_info, since,user_agent):
    number =int(number)
    text = ''
    list = search_daodao(user_info, search_time_limit, search_time_limit_num)
    handle_id = list[number - 1]['id']
    handle_data = ''
    if type == "combine":
        new_list=list[0:number]
        new_list.reverse()
        for i in new_list:
            handle_data += json.loads(i['content'])['content']
        delete_data_muti(number,user_info, search_time_limit, search_time_limit_num)
        creat_data(now_time, user_info,'{"content":"'+ handle_data+'",\n"user_agents":"'+str(user_agent)+'"}' , since)
        text ='Execution: combine the data'
    else:
        if type == "append":
            handle_data =json.loads(list[number-1]['content'])['content'] + data
            text ='Execution: append the data'
        elif type == "edit":
            handle_data = data
        if len(list) < number:
            text ='Incorrect input, please reenter!'
        else:
            change_data(user_info,handle_id, '{"content":"'+ handle_data+'",\n"user_agents":"'+str(user_agent)+'"}')
            text ='Execution: update the data'
    return text



# -------------------end

# 查询叨叨（应用） -------------------start
def search_daodao_lite(user_info, search_time_limit, search_time_limit_num):
    search_result = github_daodao_config_comments(user_info, search_time(search_time_limit))
    search_result.sort(key=return_time, reverse=True)
    result_list = []
    for i in search_result[0:search_time_limit_num]:
        this_time = datetime.strptime(i['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        item_dict = {
            # 北京时间
            # 'time': time_zone_reset(this_time, zone, '%Y-%m-%d %H:%M:%S'),
            # 时间戳
            'date': {"$date": int(TIME.mktime(this_time.timetuple()))},
            'content': json.loads(i['body'])['content'],
            'from':json.loads(i['body'])['user_agents'],
            'id': str(i['id'])
        }
        result_list.append(item_dict)
    print(result_list)
    return result_list

def search_daodao(user_info, search_time_limit, search_time_limit_num):
    search_result = github_daodao_config_comments(user_info, search_time(search_time_limit))
    search_result.sort(key=return_time, reverse=True)
    result_list = []
    for i in search_result[0:search_time_limit_num]:
        this_time = datetime.strptime(i['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        item_dict = {
            # 北京时间
            # 'time': time_zone_reset(this_time, zone, '%Y-%m-%d %H:%M:%S'),
            # 时间戳
            'date': {"$date": int(TIME.mktime(this_time.timetuple()))},
            'content': str(i['body']),
            'id': str(i['id'])
        }
        result_list.append(item_dict)
    print(result_list)
    return result_list

# -------------------end


# 公共方法 -------------------start
# yaml配置读取
def load_yaml_config(path):
    f = open(path, 'r', encoding='utf-8')
    ystr = f.read()
    ymllist = yaml.load(ystr, Loader=yaml.FullLoader)
    return ymllist

# 判断时间是否存在
def judge_time_excit(list, time):
    flag = False
    last_issue_number = 0
    for i in list:
        if int(i['number']) > int(last_issue_number):
            last_issue_number = i['number']
        if i['title'] == str(time):
            flag = True

    return {
        "flag": flag,
        "last_issue_number": last_issue_number
    }

# 读取用户日期信息 --issue
def github_daodao_config(user_info, since):
    requests_path = 'https://api.github.com/repos/' + user_info['user'] + '/' + user_info['source'] + '/issues'
    token = 'token ' + user_info['token']
    r = requests.get(requests_path,
                     headers={"User-Agent": 'curl/7.52.1',
                              'Content-Type': 'application/json',
                              'since': since,
                              'Accept': 'application/vnd.github.everest-preview+json',
                              'Authorization': token})
    return r.json()


# 读取用户评论信息 --issue
def github_daodao_config_comments(user_info, since):
    requests_path = 'https://api.github.com/repos/' + user_info['user'] + '/' + user_info['source'] + '/issues/comments'
    token = 'token ' + user_info['token']
    r = requests.get(requests_path,
                     headers={"User-Agent": 'curl/7.52.1',
                              'Content-Type': 'application/json',
                              'since': since,
                              'Accept': 'application/vnd.github.everest-preview+json',
                              'Authorization': token})
    return r.json()


# 搜索的时间区间
def search_time(number):
    time_ago = (datetime.today() - timedelta(days=number)).utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    return time_ago


# 时区重置为当前时区
def time_zone_reset(time, zone, fomat):
    time_return = (time + timedelta(hours=zone)).strftime(fomat)
    return time_return


# 时间排序使用的筛选
def return_time(i):
    return datetime.strptime(i['updated_at'], '%Y-%m-%dT%H:%M:%SZ').timestamp()

# -------------------end


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
    # 传入数据
        config = load_yaml_config('./config.yml')['setting']
    # 默认测试数据
        data = ''
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
    # 生成查询范围
        since = search_time(search_time_limit)
        
        print('当地时间为：', now_time)
        user_agent = user_agents.parse(self.headers['User-Agent'])
        o = parse.urlparse(self.path)            
        if 'k' in parse.parse_qs(o.query) :
            data = parse.parse_qs(o.query)['k'][0]
            if data == os.environ["DAODAO_PASSWORD"]:
                if 'g' in parse.parse_qs(o.query):
                    data = parse.parse_qs(o.query)['g'][0]
                    text = change_data_handle(int(data),'','combine',search_time_limit, search_time_limit_num, zone,now_time, user_info, since,user_agent)
                elif 'a' in parse.parse_qs(o.query):
                    data = parse.parse_qs(o.query)['a'][0]
                    data = data.split(',',1)
                    text = change_data_handle(int(data[0]),data[1],'append',search_time_limit, search_time_limit_num, zone,now_time, user_info, since,user_agent)
                elif 'e' in parse.parse_qs(o.query):
                    data = parse.parse_qs(o.query)['e'][0]
                    data = data.split(',',1)
                    text = change_data_handle(int(data[0]),data[1],'edit',search_time_limit, search_time_limit_num, zone,now_time, user_info, since,user_agent)
                elif 'c' in parse.parse_qs(o.query):
                    data = parse.parse_qs(o.query)['c'][0]
                    text = creat_data(now_time, user_info, '{"content":"'+ data+'",\n"user_agents":"'+str(user_agent)+'"}',  since)
                elif 'dn' in parse.parse_qs(o.query):
                    num = parse.parse_qs(o.query)['dn'][0]
                    text = delete_data_single(num,user_info, search_time_limit, search_time_limit_num)
                elif 'd' in parse.parse_qs(o.query):
                    num = parse.parse_qs(o.query)['d'][0]
                    text = delete_data_muti(num,user_info, search_time_limit, search_time_limit_num)
                else:
                    text = 'please check!'
            else:
                text='Please enter the correct password'
        elif 'q' in parse.parse_qs(o.query):
            num = int(parse.parse_qs(o.query)['q'][0])
            if num == 0:
                num = search_time_limit_num 
            if 't' in parse.parse_qs(o.query):
                limit = int(parse.parse_qs(o.query)['t'][0])
            else:
                limit = search_time_limit
            text = json.dumps(search_daodao_lite(user_info, limit, num))
        else:
            text='Please enter the correct password'
        
        self.send_response(200)
        # """ Sets headers required for CORS """
        self.send_header('Content-type', 'application/json')
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()
        self.wfile.write(text.encode())
