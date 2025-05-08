'''
代码名称：爬取人民日报数据为txt文件
编写日期：2025年1月1日
作者：github（caspiankexin）
版本：第3版
可爬取的时间范围：2024年12月起
注意：此代码仅供交流学习，不得作为其他用途。
'''


import requests
import bs4
import os
import datetime
import time
import traceback
from common.date import get_date_list
from common.web import fetchUrl
from common.file import saveFile


def getPageList(year, month, day):
    '''
    功能：获取当天报纸的各版面的链接列表
    参数：年，月，日
    '''
    url = 'https://epaper.scdaily.cn/shtml/scrb/' + year + month + day + '/v01.shtml'
    html = fetchUrl(url)
    bsobj = bs4.BeautifulSoup(html,'html.parser')
    target_div = bsobj.find('div', attrs = {'class': 'main_r'})
    # https://epaper.scdaily.cn/shtml/scrb/20250507/v01.shtml
    # 第0个ul是二维码，第1个ul是版面导航，第2个ul是版面内容
    target_ul = target_div.find_all('ul')[1]
    pageList = target_ul.find_all('p')
    linkList = []

    for page in pageList:
        link = page.a["href"]
        url = 'https://epaper.scdaily.cn' + link
        linkList.append(url)

    return linkList

def getTitleList(year, month, day, pageUrl):
    '''
    功能：获取报纸某一版面的文章链接列表
    参数：年，月，日，该版面的链接
    '''
    html = fetchUrl(pageUrl)
    bsobj = bs4.BeautifulSoup(html,'html.parser')
    target_div = bsobj.find('div', attrs = {'class': 'main_r'})
    # https://epaper.scdaily.cn/shtml/scrb/20250507/v01.shtml
    # 第0个ul是二维码，第1个ul是版面导航，第2个ul是版面内容
    target_ul = target_div.find_all('ul')[2]
    titleList = target_ul.find_all('p')
    linkList = []

    for title in titleList:
        target_a = title.find('a')
        link = target_a["href"]
        url = 'https://epaper.scdaily.cn' + link
        linkList.append(url)

    return linkList

def getContent(html):
    '''
    功能：解析 HTML 网页，获取新闻的文章内容
    参数：html 网页内容
    '''
    bsobj = bs4.BeautifulSoup(html,'html.parser')
    target_ul = bsobj.find('ul', attrs = {'class': 'news'})
    # 获取文章 标题
    h3_text = target_ul.h3.text if target_ul.h3 else ""
    h1_text = target_ul.h1.text if target_ul.h1 else ""
    h2_text = target_ul.h2.text if target_ul.h2 else ""
    title = h3_text + '\n' + h1_text + '\n' + h2_text + '\n'
    #print(title)

    # 获取文章 内容
    font_List = target_ul.find_all('font')
    content = ''
    for font in font_List:
        text_parts = []
        for element in font.contents:
            if element.name == 'br':  # 遇到 br 标签则添加换行
                text_parts.append('\n')
            else:  # 其他元素提取文本（自动处理标签嵌套）
                text_parts.append(str(element).strip())  # strip() 去除多余空白（可选）
        content += ''.join(text_parts) + '\n'
    #print(content)

    # 返回结果 标题+内容
    resp = title + content
    return resp

def download_scrb(year, month, day, destdir):
    '''
    功能：爬取《四川日报》网站 某年 某月 某日 的新闻内容，并保存在 指定目录下
    参数：年，月，日，文件保存的根目录
    '''
    pageList = getPageList(year, month, day)
    pageNo = 0
    for page in pageList:
        try:
            pageNo = pageNo + 1
            titleList = getTitleList(year, month, day, page)
            titleNo = 0
            for url in titleList:
                titleNo = titleNo + 1

                # 获取新闻文章内容
                html = fetchUrl(url)
                content = getContent(html)

                # 生成保存的文件路径及文件名
                path = destdir + '/' + year + month + day + '/'
                fileName = year + month + day + '-' + str(pageNo).zfill(2) + '-' + str(titleNo).zfill(2) + '.md'

                # 保存文件
                saveFile(content, path, fileName)
        except Exception as e:
            print(f"日期 {year}-{month}-{day} 下的版面 {page} 出现错误（类型：{type(e).__name__}）：{e}")
            print("详细堆栈跟踪：")
            print(traceback.format_exc())  # 输出异常发生的具体位置和调用链
            continue


if __name__ == '__main__':
    '''
    主函数：程序入口
    '''
    # 输入起止日期，爬取之间的新闻
    print("欢迎使用四川日报爬虫，请输入以下信息：")
    # beginDate = input('请输入开始日期:')
    # endDate = input('请输入结束日期:')
    beginDate = '20250507'
    endDate = '20250508'
    destdir = "./data/scrb"
    data = get_date_list(beginDate, endDate)

    for d in data:
        year = str(d.year)
        month = str(d.month) if d.month >=10 else '0' + str(d.month)
        day = str(d.day) if d.day >=10 else '0' + str(d.day)
        destdir = destdir  # 爬下来的文件的存储地方

        download_scrb(year, month, day, destdir)
        print("爬取完成：" + year + month + day)
        time.sleep(5)        # 怕被封 IP 爬一爬缓一缓，爬的少的话可以注释掉

    lastend = input("本次数据爬取完成!可以关闭软件了")

