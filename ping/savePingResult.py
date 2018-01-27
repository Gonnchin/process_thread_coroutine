#!/usr/bin/env python
# coding=utf-8
import subprocess
import time
from influxdb import InfluxDBClient


def testNameHandle(str):
    """处理测试例名称"""
    test_name_dst_ip = str.split('80.1.2.1.4.')[1].split(' = STRING: ')
    test_name = test_name_dst_ip[0]
    dst_ip = test_name_dst_ip[1].replace('"', '')
    result = dict()
    result[test_name] = dst_ip
    return result


# 获取交换机所有nqa实例名
def getTestName(src_ip):
    """
    1.获取交换机所有nqa实例名
        拼接下发命令
        1.snmpwalk -v 2c -c password src_ip oid+nqa实例名称
        2.通过subprocess的Popen来调用系统命令，执行命令
    2.对获取的实例名称进行处理

    :param src_ip:
    :return:
    """
    oid = '1.3.6.1.2.1.80.1.2.1.4'
    cmd_snmp = "snmpwalk -v 2c -c ucloud.cn {0} {1}".format(src_ip, oid)
    sub = subprocess.Popen(cmd_snmp, shell=True, stdout=subprocess.PIPE)
    result = sub.stdout.read().splitlines()
    test_name_ip = map(testNameHandle, result)
    test_name = [i.keys() for i in test_name_ip]
    return test_name


# 处理测试的时间
def testTimeHandle(str):
    """将16进制时间转换为‘YYYY-mm-dd hh:MM:SS:milli’格式
    07 E2 01 03 0E 2D 27 03
    :param str:
    :return:
    """
    try:
        test_time_tmp = str.split('= Hex-STRING: ')[1].strip()
    except:
        test_time_tmp = '00 00 00 00 00 00 00 00'
    test_time_list = test_time_tmp.split(' ')
    year = int(test_time_list[0]+test_time_list[1], 16)
    month = int(test_time_list[2], 16)
    day = int(test_time_list[3], 16)
    hour = int(test_time_list[4], 16)
    min = int(test_time_list[5], 16)
    sec = int(test_time_list[6], 16)
    millisec = int(test_time_list[7], 16)
    return '{year}-{month:0>2d}-{day:0>2d} {hour:0>2d}:{min:0>2d}:{sec:0>2d}:{millisec:0>2d}'.format(**vars())


# 获取时延,和测试时间
def getDelayTime(src_id, test_name):
    """

    :param src_id:
    :param test_name:
    :return:
    """
    delay_result = {}
    data = []
    delay_oid = "1.3.6.1.2.1.80.1.3.1.6" + '.' + test_name
    time_oid = "1.3.6.1.2.1.80.1.3.1.10" + '.' + test_name

    cmd_snmp = "snmpwalk -v 2c -c ucloud.cn {0} {1}".format(src_id, delay_oid)
    sub = subprocess.Popen(cmd_snmp, shell=True, stdout=subprocess.PIPE)
    result = sub.stdout.read()
    #print "delay_time: %s" % result
    try:
        delay_time = result.split('Gauge32: ')[1]
    except:
	delay_time = '0'
    data.append(delay_time.strip())

    # delay_time = map(delayTimeHandle, result)

    cmd_snmp = "snmpwalk -v 2c -c ucloud.cn {0} {1}".format(src_id, time_oid)
    sub = subprocess.Popen(cmd_snmp, shell=True, stdout=subprocess.PIPE)
    result = sub.stdout.read().splitlines()
    # 处理获取的测试时间
    #print 'str_time %s' % result
    test_time = map(testTimeHandle, result)
    data.append(test_time[0])
    delay_result[test_name] = data
    return delay_result


# 获取测试结果:ping的往返平均时间
def getPingResult(src_ip):
    """
    当前的ping往返平均时间 oid为：  1.3.6.1.2.1.80.1.3.1.6
    1.获取交换机所有nqa实例名
    2.获取交换机nqa实例对应ping的平均时间(ms)
    :return:
    """
    # 获取交换机所有nqa实例名,列表中为字典格式name:dst_ip
    test_name_list = getTestName(src_ip)
    # 获取交换机nqa实例对应ping的平均时间(ms),测试时间
    print "test_name_list: %s" % test_name_list
    ping_result = map(getDelayTime, [src_ip for i in test_name_list], [test_name[0] for test_name in test_name_list])
    print ping_result
    return ping_result


def savePingResult(src_ip):
    """将测试数据保存到influxdb
    保存内容：1.测试例oid  2.ping往返平均时间  3.测试时间
    1.获取测试数据
    2.连接influxdb，保存数据
    host=
    port=8086
    db_name=
    table_name = switch_ping_3s
    :return:
    """
    # 获取测试数据
    test_result = getPingResult(src_ip)
    #print "test_result: %s" % test_result
    # 连接influxdb，保存数据
    client = InfluxDBClient(host='192.168.153.220', port=8086, database='pingResult')
    show_table = client.query('show measurements;')
    #client.query('insert test3,name=6,delay=6 t=6;')
    print 'tables: %s' % show_table
    for data in test_result:
        instance_name = data.keys()
        delay_time = data.values()[0][0]
        test_time = data.values()[0][1]
        """UNIX时间戳
        test_time: '2018-01-10 19:12:51:03'
        strptime: time.struct_time(tm_year=2018, tm_mon=1, tm_mday=10, 
                    tm_hour=19, tm_min=12, tm_sec=51, tm_wday=2, tm_yday=10, tm_isdst=-1)
        mktime: 1515582771.0
        """
        if test_time == '0-00-00 00:00:00:00':
	    continue
        timestamps = time.mktime(time.strptime(test_time, "%Y-%m-%d %H:%M:%S:%U"))
       # timestamps = time.mktime(time.strptime(test_time, "%Y-%m-%d %H:%M:%S"))
        testResult = [
            {
                "measurement": 'test_result',
                "time": int(timestamps),
                "fields": {
                    "delay_time": delay_time
                },
                "tags": {
                    "instance_name": instance_name
                }
            }
        ]
        client.write_points(testResult)


if __name__ == '__main__':
    src_ip = '192.168.148.210'
    savePingResult(src_ip) 
