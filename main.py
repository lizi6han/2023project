import json
import csv
import requests
import re
from pyecharts import options as opts
from pyecharts.charts import Geo
from sklearn.ensemble import RandomForestRegressor
f = open('双色球.csv', mode = 'a', encoding='utf-8', newline='')
csv_writer = csv.DictWriter(f, fieldnames=['期号',
       '总销售额',
       '红球',
       '蓝球',
       '一等奖省份',])
csv_writer.writeheader()
codes,sales,loc_nums,r1,r2,r3,r4,r5,r6,b1= [[] for i in range(10)]
for page in range(1,35):
   url = 'http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice'
   params = {
       'name': 'ssq',
       'issueCount': '1000',
       'issueStart':'',
       'issueEnd':'',
       'dayStart':'',
       'dayEnd':'',
       'pageNo': page,
       'pageSize': '30',
       'week':'',
       'systemType': 'PC',
   }
   headers = {
       'Cookie':'HMF_CI=82ac1717019be06612a807a78d62dca4174df36c5cee955e0868e54b14275d399f5a4247f0b43ba953c5a2e30d8c703191964bfb88a519bc3bf309ec01f93bd832; 21_vq=14',
       'Referer':'http://www.cwl.gov.cn/ygkj/wqkjgg/ssq/',
       'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67'
   }
   response = requests.get(url=url, params=params, headers=headers)
   result = response.json()['result']
   for index in result:

       content = index['content'].replace('注', '')  # 字符串处理
       tam = content.find('。')
       if tam != -1:
           content = content[: tam]


       content = content.split(',')  # 分割
       content = content[:-1]
       loc = []  # 将地区与中奖个数分割
       num = []
       loc_num = {}

       for x in content:
           loc.append(re.sub(r'[0-9]+', '', x))
           num.append(re.sub(u'[^0-9]+', '', x))

       for key, value in zip(loc, num):
           loc_num[key] = value
       loc_nums.append(loc_num)

       # 红球号码
       red = index['red'].split(',')
       r1.append(int(red[0]))
       r2.append(int(red[1]))
       r3.append(int(red[2]))
       r4.append(int(red[3]))
       r5.append(int(red[4]))
       r6.append(int(red[5]))
       # 篮球号码
       blue = index['blue']
       b1.append(int(blue))
       dit = {
           '期号': index['code'],
           '总销售额' : index['sales'],
           '红球': index['red'],
           '蓝球': index['blue'],
           '一等奖省份': index['content'],
       }

       csv_writer.writerow(dit)
       print(dit)
loc_nums_total={}
for x in loc_nums:
   for k in x.keys():
       if k not in loc_nums_total.keys():
           loc_nums_total[k]=0
       loc_nums_total[k]=loc_nums_total[k]+int(x[k])

print(loc_nums_total)
loc_nums_totals=[]
for key,value in loc_nums_total.items():
   loc_nums_totals.append((key,value))

print(loc_nums_totals)
def create_china_map():
   (
       #初始化地图并设置地图大小
       Geo(init_opts=opts.InitOpts(width="1000px", height="900px"))
       # 选择中国地图模板
       .add_schema(maptype='china')
       # 设置系列名称和数据项
       .add(series_name='中奖数量',data_pair=loc_nums_totals,)

       # 将标签名称显示为省名称
       .set_series_opts(label_opts=opts.LabelOpts(is_show=True,formatter='{b}'))
       # 全局配置项
       .set_global_opts(
           title_opts=opts.TitleOpts(title="双色球1000期各省中奖数量"),

           visualmap_opts=opts.VisualMapOpts(
                pieces=pieces,
                is_piecewise=True,
                is_show=True
           )
       )


       # 生成本地html文件
       .render("双色球.html")
   )
pieces = [
       {'max': 0, 'label': '0以下', 'color': '#50A3BA'},
       {'min': 1, 'max': 100, 'label': '1-10', 'color': '#3700A4'},
       {'min': 101, 'max': 200, 'label': '72-74', 'color': '   #FF0000'},     #红色
       {'min': 201, 'max': 300, 'label': '110-112', 'color': '#FF8C00'},  #橙色
       {'min': 301, 'max': 400, 'label': '30-50', 'color': '#FCF84D'},
       {'min': 401, 'max': 500, 'label': '50-100', 'color': '#DD0200'},
       {'min':501, 'max': 800, 'label': '150-155', 'color': '#00CED1'},   #绿色
       {'min':801, 'max': 1000, 'label': '190-192', 'color': '#0000FF'}   #  蓝色
   ]

create_china_map()

pre_num={}

#随机森林回归模型
def get_predicted_nums(lotto):
   X = []
   y = []
   for i in range(1, len(lotto)):
       X.append([lotto[i-1]])
       y.append(lotto[i])

   model = RandomForestRegressor(n_estimators=1000)
   model.fit(X, y)

   predicted_nums = model.predict([[lotto[-1]]])
   return predicted_nums

print('预测下一个红1为：', int(get_predicted_nums(r1)))
print('预测下一个红2为：', int(get_predicted_nums(r2)))
print('预测下一个红3为：', int(get_predicted_nums(r3)))
print('预测下一个红4为：', int(get_predicted_nums(r4)))
print('预测下一个红5为：', int(get_predicted_nums(r5)))
print('预测下一个红6为：', int(get_predicted_nums(r6)))
print('预测下一个蓝1为：', int(get_predicted_nums(b1)))

#统计
def get_predicted_num(lotto, lotto_id):
    dit_num={}
    for i in lotto:
        if i not in dit_num.keys():
            dit_num[i]=0
        dit_num[i]=dit_num[i]+1
    ans = max(dit_num, key=lambda x: dit_num[x])
    if lotto_id < 7:
        print(f'中奖第{lotto_id}个红球为：', ans, '号球')
    else:
        print('中奖蓝球为：',ans, '号球')


print('统计预测：')
get_predicted_num(r1, 1)  # 预测红1
get_predicted_num(r2, 2)  # 预测红2
get_predicted_num(r3, 3)  # 预测红3
get_predicted_num(r4, 4)  # 预测红4
get_predicted_num(r5, 5)  # 预测红5
get_predicted_num(r6, 6)  # 预测红6
get_predicted_num(b1, 7)  # 预测蓝7