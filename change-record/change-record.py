#!/usr/bin/env python
# encoding: utf-8

from dnspod.apicn import *
from pprint import pprint
import sys
import re
import json
import os

reload(sys)
sys.setdefaultencoding('utf8')


class DomainInfo(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.domains = dict()
        self.recordlist = list()
        self.records = list()
        self.data = list()

    def __error_status(self,msg, status_type):
        print msg
        sys.exit(int(status_type))

    def __get_domain_id(self):
        '''
        获取该帐号下所以域名的 domain_id 和 domain_name
            return ==> {'ximigame.com': {'sub_domain': [], 'domain_id': 1111}}
        '''
        api = DomainList(email=self.email, password=self.password)
        result = api()
        result_status = result['status']['code']
        if result_status == u'1':
            for domain in result['domains']:
                dname = domain['name']
                did = domain['id']
                #domains.setdefault(domain_name=dname, domain_id=did)
                self.domains.setdefault(dname, dict(domain_id=did, sub_domain=list()))
        else:
            msg = "响应代码:\n6 记录开始的偏移无效\n7 共要获取的记录的数量无效\n9 没有任何域名"
            self.__error_status(msg, result_status)

    def __get_record_list(self, domain_id):
        '''
        获取该域名下所以解析记录信息
            retun [{domain_id:1111, domain_name:ximigame.com, sub_domain:www, record_id:2222, record_type:A, record_line:电信, value:'1.1.1.1',ttl:600}]
        '''
        api = RecordList(domain_id, email=self.email, password=self.password)
        result = api()
        result_status = result['status']['code']
        domain_id = result['domain']['id']
        domain_name = result['domain']['name']

        if result_status == u'1':
            for record in result['records']:
                sub_domain = record['name']
                record_id = record['id']
                record_type = record['type']
                record_line = record['line'].encode('utf-8')
                value = record['value']
                ttl = record['ttl']
                self.recordlist.append(dict(domain_id=domain_id, domain_name=domain_name, sub_domain=sub_domain, record_id=record_id, record_type=record_type, record_line=record_line, value=value, ttl=ttl))
        else:
            msg = "响应代码:\n-7 企业账号的域名需要升级才能设置\n-8 代理名下用户的域名需要升级才能设置\n6 域名ID错误\n7 记录开始的偏移无效\n8 共要获取的记录的数量无效\n9 不是域名所有者\n10 没有记录"
            self.__error_status(msg, result_status)

    def GetDomainList(self, domainlist):
        '''
        清理用不上的域名,只保留有用的域名
            update: {'ximigame.com': {'sub_domain': ['www','abc'], 'domain_id': 1111}}
        '''
        self.__get_domain_id()

        for domain in domainlist:
            sub_domain, domain = split_domain(domain)
            self.domains[domain]['sub_domain'].append(sub_domain)

        for domain, opts in self.domains.items():
            if len(opts['sub_domain']) == 0:
                self.domains.pop(domain)

    def GetRecordsList(self):
        '清理用不上的记录,只保留有用的记录'
        for domain in self.domains.values():
            domain_id = domain['domain_id']
            self.__get_record_list(domain_id)

            for sub_domain in domain['sub_domain']:
                for record in self.recordlist:
                    if (sub_domain == record['sub_domain']) and (domain_id == record['domain_id']):
                        self.records.append(record)

    def CreateRecord(self, record):
        '添加解析记录'
        domain_name = record['domain_name']
        sub_domain = record['sub_domain']
        record_type = record['record_type']
        record_line = record['record_line']
        value = record['value']
        ttl = int(record['ttl'])
        domain_id = record['domain_id']

        api = RecordCreate(sub_domain, record_type, record_line, value, ttl, domain_id=domain_id, email=self.email, password=self.password)
        result = api()
        result_status = result['status']['code']

        if result_status == u'1':
            print sub_domain + '.' + domain_name, '-', result['status']['message'], '-', result['record']
        else:
            msg = 'status_code: %s\n响应代码\n-15 域名已被封禁\n-7 企业账号的域名需要升级才能设置\n-8 代理名下用户的域名需要升级才能设置\n6 缺少参数或者参数错误\n7 不是域名所有者或者没有权限\n21 域名被锁定\n22 子域名不合法\n23 子域名级数超出限制\n24 泛解析子域名错误\n500025 A记录负载均衡超出限制\n500026 CNAME记录负载均衡超出限制\n26 记录线路错误\n27 记录类型错误\n30 MX 值错误，1-20\n31 存在冲突的记录(A记录、CNAME记录、URL记录不能共存)\n32 记录的TTL值超出了限制\n33 AAAA 记录数超出限制\n34 记录值非法\n36 @主机的NS纪录只能添加默认线路\n82 不能添加黑名单中的IP' %(result_status)
            print msg

    def ChangeRecord(self, record):
        '修改记录解析配置'
        domain_name = record['domain_name']
        sub_domain = record['sub_domain']
        record_id = int(record['record_id'])
        record_type = record['record_type']
        record_line = record['record_line']
        value = record['value']
        ttl = int(record['ttl'])
        domain_id = record['domain_id']

        api = RecordModify(sub_domain, record_id, record_type, record_line, value, ttl, domain_id=domain_id, email=self.email, password=self.password)
        result = api()
        result_status = result['status']['code']

        if result_status == u'1':
            print sub_domain + '.' + domain_name, '-', result['status']['message'], '-', result['record']
        else:
            msg = 'status_code: %s\n响应代码\n-15 域名已被封禁\n-7 企业账号的域名需要升级才能设置\n-8 代理名下用户的域名需要升级才能设置\n6 域名ID错误\n7 不是域名所有者或没有权限\n8 记录ID错误\n21 域名被锁定\n22 子域名不合法\n23 子域名级数超出限制\n24 泛解析子域名错误\n500025 A记录负载均衡超出限制\n500026 CNAME记录负载均衡超出限制\n26 记录线路错误\n27 记录类型错误\n29 TTL 值太小\n30 MX 值错误，1-20\n31 URL记录数超出限制\n32 NS 记录数超出限制\n33 AAAA 记录数超出限制\n34 记录值非法\n35 添加的IP不允许\n36 @主机的NS纪录只能添加默认线路\n82 不能添加黑名单中的IP' %(result_status)
            # self.__error_status(msg, result_status)
            print msg

    def DeleteRecord(self, record):
        domain_id = record['domain_id']
        record_id = int(record['record_id'])
        sub_domain = record['sub_domain']
        domain_name = record['domain_name']

        api = RecordRemove(domain_id, record_id, email=self.email, password=self.password)
        result = api()
        result_status = result['status']['code']

        if result_status == u'1':
            print sub_domain + '.' + domain_name, '-', result['status']['message'], '-', result['record']
        else:
            msg = 'status_code: %s\n响应代码\n-15 域名已被封禁\n-7 企业账号的域名需要升级才能设置\n-8 代理名下用户的域名需要升级才能设置\n6 域名ID错误\n7 不是域名所有者或没有权限\n8 记录ID错误\n21 域名被锁定' %result_status
            print msg

#############################

def split_domain(domain):
    '''
    拆分主机头和根域名:
        www.abc.com     ==>     (www, abc.com)
    '''
    pattern = re.compile(r'(.*?)\.([^\.]+\.net|[^\.]+\.com|[^\.]+\.cn)', re.I)
    match = pattern.match(domain)
    if match:
        return match.groups()
    else:
        print "%s: 匹配失败" %domain

#############################

def main(mode):
    if mode == 'get':
        with open(domain_list_file, 'r') as f:
            domainlist = f.read().splitlines()

        d = DomainInfo(email, password)
        d.GetDomainList(domainlist)
        d.GetRecordsList()

        jsonstr = json.dumps(d.records, sort_keys=True, indent=4, ensure_ascii=False)
        with open(ol_conf_file, 'w') as f:
            f.writelines(jsonstr)

    elif mode == 'up':
        with open(local_conf_file, 'r') as f:
            records = json.loads(f.read())

        d = DomainInfo(email, password)
        for record in records:
            d.ChangeRecord(record)

    elif mode == 'cr':
        with open(local_conf_file, 'r') as f:
            records = json.loads(f.read())

        d = DomainInfo(email, password)
        for record in records:
            d.CreateRecord(record)

    elif mode == 'del':
        with open(local_conf_file, 'r') as f:
            records = json.loads(f.read())

        d = DomainInfo(email, password)
        for record in records:
            d.CreateRecord(record)

    else:
        print """
        Usage:
            python {0} get                  - 获取域名列表(domain.list)里域名的线上配置,并写入文件(online-config.json)
            python {0} up <file>            - 同步本地配置列表<file>里的配置到线上(dnspod).
            python {0} cr <file>            - 创建新的主机记录.
            python {0} del <file>           - 删除线上主机记录.
        """.format(sys.argv[0])

#############################

if __name__ == '__main__':

    email = "your email"
    password = "your password"

    dirname = os.path.abspath(os.path.dirname(__file__)) + '/'
    domain_list_file = dirname + "get-domain.list"
    ol_conf_file = dirname + "online-config.json"

    mode = sys.argv[1] if len(sys.argv) > 1 else None
    local_conf_file = sys.argv[2] if  (mode == 'up') or (mode == 'cr') or (mode == 'del') else None

    main(mode)
