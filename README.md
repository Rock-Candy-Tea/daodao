# 叨叨点啥
哔哔点啥的白嫖版本。基于github的issue及vercel api搭建。

### ios 快捷指令 
https://www.icloud.com/shortcuts/06fc462d4b4b4f668b16cb11e2e9d010
___

### config设置：
```yml
setting:
  zone: 8 #时区校准
  search_time_limit: 3 #默认最大查询时间范围3天
  search_time_limit_num: 5 #默认查询条数5条
  user: 'zfour' #用户名
  repo: 'daodao'  #用户仓库
```

### vercel环境变量设置:

![image](https://user-images.githubusercontent.com/19563906/112720871-ddaee080-8f3b-11eb-92ea-a5c567eb2293.png)

<b>DAODAO_PASSWORD</b> 

自定义密码，用于验证写、改、删等操作。<br>

<b>DAODAO_TOKEN</b> 

github的查询token（https://github.com/settings/tokens）。

### 查询参数及示例:

#### q （无需输入密码）

请求连接: {vercle项目链接}/api?q={number1}&t={number2}

示例: https://daodao-three.vercel.app/api?q=5

number1(必填): 为0的时候取config值

number2(选填): 查询的时间范围，单位天

#### k （密码）
密码参数，以下查询均需

#### c 增加一条叨叨（需输入密码）
请求连接: {vercle项目链接}/api?c={content}&k={key}

示例: https://daodao-three.vercel.app/api?c=这是一条测试&k=******

content: 可以是文字或者html代码

#### d 删除一条/n条最新的叨叨（需输入密码）
请求连接: {vercle项目链接}/api?d={number}&k={key}

示例: https://daodao-three.vercel.app/api?d=1&k=******

number: 正整数

#### dn 删除第一条/n条最新的叨叨（需输入密码）
请求连接: {vercle项目链接}/api?dn={number}&k={key}

示例: https://daodao-three.vercel.app/api?dn=2&k=******

number: 正整数

#### a 给第n条叨叨增加内容（需输入密码）
请求连接: {vercle项目链接}/api?a={number,content}&k={key}

示例: https://daodao-three.vercel.app/api?a=2,我给第二条增加内容&k=******

number: 正整数

content: 可以是文字或者html代码

#### e 编辑第n条叨叨替换内容（需输入密码）
请求连接: {vercle项目链接}/api?e={number,content}&k={key}

示例: https://daodao-three.vercel.app/api?e=2,我给第二条替换内容&k=******

number: 正整数

content: 可以是文字或者html代码


#### g 合并最新的n条叨叨内容（需输入密码）
请求连接: {vercle项目链接}/api?g={number}&k={key}

示例: https://daodao-three.vercel.app/api?g=2&k=******

number: 正整数









