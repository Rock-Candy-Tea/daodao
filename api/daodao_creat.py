import daodao as DAODAO
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib import parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 传入数据
        config = DAODAO.load_yaml_config('config.yml')['setting']
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
            "token": config['token'],
            "user": config['user'],
            "source": config['repo']
        }
        # 生成当前时区时间标题
        now_time = DAODAO.time_zone_reset(now, zone, '%Y-%m-%d')
        # 生成查询范围
        since = DAODAO.search_time(search_time_limit)
        print('当地时间为：', now_time)
        o = parse.urlparse(self.path)
        if parse.parse_qs(o.query)['data'][0] != '':
            data = parse.parse_qs(o.query)['data'][0]
            text = DAODAO.creat_data(now_time, user_info, data, since)
        else:
            text = '请检查参数！'
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(text.encode())
        return
