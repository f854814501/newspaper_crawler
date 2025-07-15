from flask import Flask, render_template, request
from flask import Flask, render_template, request, jsonify
from common.date import get_date_list
import chengdu_daily
import people_daily
import sichuan_daily

current_progress = {'status': '未开始', 'date': ''}

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_crawl', methods=['POST'])
def start_crawl():
    newspapers_dict = {
        'chengdu': '成都日报',
        'people': '人民日报',
        'sichuan': '四川日报'
    }
    newspapers = request.form.getlist('newspaper[]')
    begin_date = request.form['beginDate'].replace('-', '')  # 转换为YYYYMMDD格式
    end_date = request.form['endDate'].replace('-', '')
    date_list = get_date_list(begin_date, end_date)

    for newspaper in newspapers:
        destdir = './data/' + newspaper  # 根据报纸类型区分存储目录
        for d in date_list:
            year = str(d.year)
            month = str(d.month).zfill(2)
            day = str(d.day).zfill(2)
            current_date = f'{year}年{month}月{day}日'
            current_progress['status'] = f'正在爬取{newspapers_dict[newspaper]}{current_date}的数据'
            current_progress['date'] = current_date
            if newspaper == 'chengdu':
                chengdu_daily.download_cdrb(year, month, day, destdir)
            elif newspaper == 'people':
                people_daily.download_rmrb(year, month, day, destdir)
            elif newspaper == 'sichuan':
                sichuan_daily.download_scrb(year, month, day, destdir)
            current_progress['status'] = f'{current_date}数据已爬取'

    current_progress['status'] = '爬取任务执行完成'
    return '爬取任务执行完成'

@app.route('/get_progress')
def get_progress():
    return jsonify(current_progress)

# 添加main函数入口
if __name__ == '__main__':
    app.run(debug=False)  # 启动Flask开发服务器（调试模式）