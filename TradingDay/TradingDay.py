# -*- coding: utf-8 -*-
"""
Created on Sun Jun 12 17:32:16 2022

@author: blainetang
"""

import pandas as pd
import datetime
import numpy as np
from lunardate import LunarDate
hlds=pd.read_csv('holidays.txt')
# 将DataFrame格式变为Series格式，从而是之后的nparray满足CustomBusinessDay的格式要求
hlds=pd.Series(hlds.holidays.values)
def formatchange(time):
    """
    将holidays内的时间改为datetime格式，满足CustomBusinessDay的格式要求
    :time:holidays文件内的时间
    """
    time1=datetime.datetime.strptime(time,"%Y/%m/%d")
    return time1
holidays=hlds.apply(formatchange)
holidays=np.array(holidays)
weekdays= pd.offsets.CustomBusinessDay(holidays=holidays)  #定义新的工作日（交易日）
def timeformat(a):
    """
    将标准格式的字符串转为datetime格式，满足既可以输入str也可以输入datetime格式的需求
    :a:时间
    """
    if type(a)==str:
        b=formatchange(a)
    elif type(a)==datetime.datetime or type(a)==datetime.date:
        b=a
    else:
        print('format is wrong')
    return b
def lunarmonthsub(y,m,today):
    """
    计算农历日期
    :y:回溯到y年前
    :m:回溯到m月前
    :today:输入的日子 LuanrDate格式
    """
    lunar=LunarDate(2000,10,10)
    lunar.day=today.day
    # 因为有的农历月没有30号，所以遇到30号，减数与被减数同时前移一天
    if today.day==30:
        today=today-datetime.timedelta(days=1)
        lunar.day=today.day
        if m>=today.month:  # 如果月份比当前月大，向年份借1 凑12月
            lunar.year=today.year-1
            lunar.month=12+today.month-m
        else:
            lunar.month=today.month-m
        lunar.year=today.year-y
        days=today-lunar
    else:
        if m>=today.month:
            lunar.year=today.year-1
            lunar.month=12+today.month-m
        else:
            lunar.month=today.month-m
        lunar.year=today.year-y
        days=today-lunar
    return days
class TradingDay():
    """
    定义TradigDay类，集成所有功能
    """
    global istradingday
    def istradingday(a):
        """
        判断是否是交易日，看交易日条件下的daterange[a:a]是不是空
        :a:日期
        """
        a=timeformat(a)
        b=pd.date_range(start=a,end=a,freq=weekdays)
        if len(b)==0:
            c=False
        else:
            c=True
        return c
    def findtradingdays(self,a,b):
        """
        寻找日期区间[a,b]内的交易日
        :a:开始日期
        :b:结束日期
        """
        a=timeformat(a)
        b=timeformat(b)
        tdaylist=pd.date_range(start=a,end=b,freq=weekdays)
        return tdaylist
    global caltradingday
    def caltradingday(a,b):
        """
        计算日期a之前和之后的交易日
        :a:日期
        :b:选择"+"或"-"
        """
        a=timeformat(a)
        if b=='+':
            c=a+weekdays
        elif b=='-':
            c=a-weekdays
        else:
            print('format is wrong')
        return c
    def calsolardate(self,a,y,m,d):
        """
        计算日期 a按阳历y年m月d天前的交易日
        :a:日期（阳历）
        :y:按阳历回溯到y年前
        :m:按阳历回溯到m月前
        :d:按阳历回溯到d日前
        """
        a=timeformat(a)
        c=a-pd.DateOffset(years=y,months=m,days=d)
        c=c.to_pydatetime()
        if istradingday(c):
            re=c
        else:
            re=caltradingday(c,'+')
        return re
    def callunardate(self,y,m,d,today):
        """
        计算日期 a按农历y年m月d天前的交易日
        :a:日期（农历，LunarDate格式）
        :y:按农历回溯到y年前
        :m:按农历回溯到m月前
        :d:按农历回溯到d日前
        """
        lunar=LunarDate(2000,10,10)
        lunar.day=today.day
        if today.isLeapMonth:
            days1=datetime.timedelta(days=today.day)
            today=today-days1
            lunar=today
            monthday=lunarmonthsub(y,m,today)
            days=monthday+datetime.timedelta(days=d)+days1
        else:
            monthday=lunarmonthsub(y,m,today)
            days=monthday+datetime.timedelta(days=d)
            lunar=today-days
            c=lunar.toSolarDate()
            if istradingday(c):
                re=c
            else:
                re=caltradingday(c,'+')
        return re
    def nexttradingday(self):
        """
        计算今天之后的下一个交易日
        """
        c=datetime.datetime.now().date()+weekdays
        return c
day=TradingDay()
print('2020/1/1是交易日吗？',istradingday('2020/1/1'))
print('输出2020/1/1与2021/1/1之间的交易日：',day.findtradingdays('2020/1/1','2021/1/1'))
print('2022年6月5日之后的第一个交易日：',caltradingday(datetime.datetime(2022,6,5),'+'))
print('2022年6月5日之前的第一个交易日：',caltradingday(datetime.datetime(2022,6,5),'-'))
print('按阳历计算，2022年6月5日一年一个月一天前的交易日：',day.calsolardate(datetime.datetime(2022,6,5),1,1,1))
print('按阴历计算，2020年一月初一 一年一个月一天前的交易日：',day.callunardate(1,1,1,LunarDate(2020,1,1)))
print('下一个交易日是：',day.nexttradingday())
