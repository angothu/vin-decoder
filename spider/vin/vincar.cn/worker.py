#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import sys
import json
import os
import time

from pymongo import *

ROOT_DIR = os.path.dirname(__file__)
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, '../../../rabbitmq'))

from rabbitmq import RabbitMQ
from robot import robot_html
from parse import parse_html

timeout = 60

client = MongoClient()
client = MongoClient("localhost", 27017)
db = client["vin"]
collection = db["vin"]


def do_task(vin_code):
    print "do_task(): %s" % (vin_code)
    html = robot_html(vin_code)
    if html is not None:
        results = parse_html(html)  
        return results
    else:
        print "[2] %s not found, download page failed" % (vin_code)
    return None


def peek_task(vin_code):
    data = do_task(vin_code)
    print "result: %s" % (data)

def loop_task():
    mq = RabbitMQ(queue="vin")
    while True:
        vin_code = mq.basic_get()
        if vin_code:
            print "vinCode: %s" % (vin_code)
            results = do_task(vin_code)
            for result in results:
                result["vinCode"] = vin_code[0:8]
                collection.insert(result)
            if len(result) == 0:
                # Requeue
                mq.publish(vin_code)
            print "result: %s" % (results)
        else:
            print "no topic, to sleep 10 sec ..."
            time.sleep(10)
        time.sleep(5)

def main():
    if len(sys.argv) == 2:
        vin_code = sys.argv[1]
        peek_task(vin_code)
    else:
        loop_task()
    
if __name__ == '__main__':
    main()
