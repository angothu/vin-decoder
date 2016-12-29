#!/usr/bin/python

# -*- coding: UTF-8 -*-

import sys
import os
import time
import requests
import ipaddress
from bs4 import BeautifulSoup

ROOT_DIR = os.path.dirname(__file__)
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, '../../../rabbitmq'))
sys.path.append(os.path.join(ROOT_DIR, '../../../proxy'))

from rabbitmq import RabbitMQ
from downloader import get_page

timeout = 10
headers_default = {
    "Pragma": "no-cache",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
}

def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.findAll('table')
    table = tables[0]
    mq = RabbitMQ(queue="nianshao")
    for tr in table.findAll('tr')[1:]:
        tds = tr.findAll('td')
        if tds:
            ip = tds[0].string
            port = tds[1].string
            content = "%s:%s" %(ip, port)
            print content
            try:
                ip_tmp = ipaddress.IPv4Address(ip.decode("utf-8"))
                if ip_tmp.is_private or ip_tmp.is_reserved or ip_tmp.is_multicast:
                    print "private,reserved,multicast is not valid"
                    continue
            except ipaddress.AddressValueError, msg:
                print msg
                continue
            mq.publish(content)


def main():
    home_url = "http://www.nianshao.me/?stype=1"

    while True:
        html = get_page(home_url)
        if html is not None:
            parse_html(html)
        time.sleep(60)

if __name__ == '__main__':
    main()