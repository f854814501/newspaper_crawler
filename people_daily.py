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
    url = 'http://paper.people.com.cn/rmrb/pc/layout/' + year + month + '/' + day + '/node_01.html'
    html = fetchUrl(url)
    bsobj = bs4.BeautifulSoup(html,'html.parser')
    temp = bsobj.find('div', attrs = {'id': 'pageList'})
    if temp:
        pageList = temp.ul.find_all('div', attrs = {'class': 'right_title-name'})
    else:
        pageList = bsobj.find('div', attrs = {'class': 'swiper-container'}).find_all('div', attrs = {'class': 'swiper-slide'})
    linkList = []

    for page in pageList:
        link = page.a["href"]
        url = 'http://paper.people.com.cn/rmrb/pc/layout/'  + year + month + '/' + day + '/' + link
        linkList.append(url)

    return linkList

def getTitleList(year, month, day, pageUrl):
    '''
    功能：获取报纸某一版面的文章链接列表
    参数：年，月，日，该版面的链接
    '''
    html = fetchUrl(pageUrl)
    bsobj = bs4.BeautifulSoup(html,'html.parser')
    temp = bsobj.find('div', attrs = {'id': 'titleList'})
    if temp:
        titleList = temp.ul.find_all('li')
    else:
        titleList = bsobj.find('ul', attrs = {'class': 'news-list'}).find_all('li')
    linkList = []

    for title in titleList:
        tempList = title.find_all('a')
        for temp in tempList:
            link = temp["href"]
            if 'content' in link:
                url = 'http://paper.people.com.cn/rmrb/pc/content/' + year + month + '/' + day + '/' + link
                linkList.append(url)

    return linkList

def getContent(html):
    '''
    功能：解析 HTML 网页，获取新闻的文章内容
    参数：html 网页内容
    '''
    bsobj = bs4.BeautifulSoup(html,'html.parser')

    # 获取文章 标题
    title = bsobj.h3.text + '\n' + bsobj.h1.text + '\n' + bsobj.h2.text + '\n'
    #print(title)

    # 获取文章 内容
    pList = bsobj.find('div', attrs = {'id': 'ozoom'}).find_all('p')
    content = ''
    for p in pList:
        content += p.text + '\n'
    #print(content)

    # 返回结果 标题+内容
    resp = title + content
    return resp

def download_rmrb(year, month, day, destdir):
    '''
    功能：爬取《人民日报》网站 某年 某月 某日 的新闻内容，并保存在 指定目录下
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
    print("欢迎使用人民日报爬虫，请输入以下信息：")
    # beginDate = input('请输入开始日期:')
    # endDate = input('请输入结束日期:')
    beginDate = '20250507'
    endDate = '20250508'
    destdir = "./data/rmrb"
    data = get_date_list(beginDate, endDate)

    for d in data:
        year = str(d.year)
        month = str(d.month) if d.month >=10 else '0' + str(d.month)
        day = str(d.day) if d.day >=10 else '0' + str(d.day)
        destdir = destdir  # 爬下来的文件的存储地方

        download_rmrb(year, month, day, destdir)
        print("爬取完成：" + year + month + day)
        time.sleep(5)        # 怕被封 IP 爬一爬缓一缓，爬的少的话可以注释掉

    lastend = input("本次数据爬取完成!可以关闭软件了")

