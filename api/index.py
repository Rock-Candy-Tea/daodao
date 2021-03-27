# -*- coding: UTF-8 -*-
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
        text = '执行:今日已发送叨叨，查找issue，添加评论！'
        creat_a_new_comments(user_info, judegement['last_issue_number'], data)
    else:
        text = '执行:今日未发送叨叨，新建issue，添加评论！'
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
def delete_data(data_id):
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
def delete_data_muti(number, search_time_limit, search_time_limit_num, zone):
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
        text= '已删除最新'+handle_number+'条叨叨!'
    else:
        text='你居然一条叨叨都没有了！'
    return text


# -------------------end

# 改动叨叨 -------------------start
# 基础封装
def change_data(data_id, data):
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
def change_data_handle(number, data, type, search_time_limit, search_time_limit_num, zone, now_time, user_info, since):
    text = ''
    list = search_daodao(search_time_limit, search_time_limit_num, zone)
    handle_id = list[number - 1]['id']
    handle_data = ''
    if type == "combine":
        for i in list[0:number]:
            handle_data += list[number - 1]['content']
        delete_data_muti(number, search_time_limit, search_time_limit_num, zone)
        creat_data(now_time, user_info, handle_data, since)
    else:
        if type == "append":
            handle_data = list[number - 1]['content'] + data
        elif type == "edit":
            handle_data = data
        if len(list) < number:
            text ='输入错误，请重新输入！'
        else:
            change_data(handle_id, handle_data)
            text ='已更新第%s条叨叨为%s' % (str(number), handle_data)
    return text



# -------------------end

# 查询叨叨 -------------------start
def search_daodao(search_time_limit, search_time_limit_num, zone):
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
            'content': i['body'],
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


# 读取用户信息
def user_info(token, user, source):
    return {
        "token": token,
        "user": user,
        "source": source
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
        config = load_yaml_config('config.yml')['setting']
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
    # 生成查询范围
        since = search_time(search_time_limit)

        print('当地时间为：', now_time)

        o = parse.urlparse(self.path)
        if parse.parse_qs(o.query)['creat']:
            data = parse.parse_qs(o.query)['creat'][0]
            text = creat_data(now_time, user_info, data, since)
        if parse.parse_qs(o.query)['delete']:
            num = parse.parse_qs(o.query)['delete'][0]
            text = delete_data_muti(num,search_time_limit, search_time_limit_num, zone)
        else:
            text = 'please check!'

        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(text.encode())
    # 增加一条叨叨
    #creat_data(now_time, user_info, data,since)
    # 查询m天前的n条叨叨
    #search_result = search_daodao(search_time_limit, search_time_limit_num, zone)
    # 删除指定id叨叨
    # delete_data('808357648')
    # 删除最新n条叨叨
    #delete_data_muti(1,search_time_limit, search_time_limit_num, zone)
    # 改动最新的第i条叨叨
    # append 加字符串
    # edit 修改字符串
    # combine 结合字符串
    #change_data_handle(2,data,'combine',search_time_limit, search_time_limit_num, zone,now_time, user_info, since)
