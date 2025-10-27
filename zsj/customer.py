import json
import threading

import requests
from gevent.thread import lock
from requests.auth import HTTPBasicAuth

from util.api_call import ApiCall
from util.base64utils import Base64Utils
from util.constants import DataSyncCode
from util.mysql_ssh_utils import MySqlSSH
from zsj.common import read_json_to_list
import zsj.data_sync as data_sync


# 查询客户信息
def get_customer(cust_code):
    query_url = 'http://soa.chinagasholdings.com:7011/services/F00100000011'
    username = 'OSB_PRD_BIP'
    password = 'BipPrdq6mx#42'
    auth = HTTPBasicAuth(username, password)

    # 查询参数
    # {"parameters":{"short_code":"","account_number":"C69508603","account_name":"","fm_last_update_date":"","to_last_update_date":""}}
    biz_data = json.dumps({
        "parameters": {
            "short_code": "",
            "account_number": cust_code,
            "account_name": "",
            "fm_last_update_date": "",
            "to_last_update_date": ""
        }
    })
    base64_data = Base64Utils.base64_encode(biz_data)

    req_data = json.dumps(
        {
            "comm_ws":
                {
                    "@xmlns": "http://xmlns.oracle.com/apps/per/rest/comm_ws/invokeebsws",
                    "RESTHeader":
                        {
                            "xmlns": "http://xmlns.oracle.com/apps/per/rest/comm_ws/header",
                            "Responsibility": "CG_CUX_WS_RESP",
                            "RespApplication": "CUX",
                            "SecurityGroup": "STANDARD",
                            "NLSLanguage": "SIMPLIFIED CHINESE",
                            "Org_Id": "0"
                        },
                    "InputParameters":
                        {
                            "P_IFACE_CODE": "10BIP_AR_CUST",
                            "P_BATCH_NUMBER": "00100202308100111",
                            "P_REQUEST_DATA": base64_data
                        }
                }
        }
    )
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'User-Agent':'PostmanRuntime/7.42.0'
    }

    customer_data = None
    try:
        response = requests.post(query_url, json=json.loads(req_data), headers=headers, auth=auth)
        if response.status_code == 200:
            # print('Request was successful. 客户编码【{}】'.format(cust_code))
            back_data = json.loads(response.text)
            customer_data = Base64Utils.base64_decode(back_data["OutputParameters"]["X_RESPONSE_DATA"])
        else:
            print('Request failed {}', response.status_code)
    except requests.exceptions.RequestException as e:
        print('An error occurred:', e)

    print(customer_data)
    return json.loads(customer_data)

# 批量分配适用范围
def customer_adapter_batch(cust_codes):
    # 数据库连接
    database = MySqlSSH()

    for cust_code in cust_codes:
        customer_adapter(cust_code, database)

    database.close()

# 分配适用范围
def customer_adapter(cust_code, database):
    customer_data = get_customer(cust_code)

    cust0 = customer_data["cust"][0]
    # 客户基础信息
    cust_base = cust0["customer"]
    # 客户编码
    insert_cust_code = cust_base["account_number"]
    # 客户id
    sql = "select id from iuap_apdoc_coredoc.merchant where cCode = '{}'".format(insert_cust_code)
    cust_rows = database.fetch_all(sql)
    if not cust_rows:
        return
    cust_id = [row[0] for row in cust_rows][0]

    # 客户往来公司（适用范围）
    ou_datas = cust0["site"]
    ou_codes = []
    if ou_datas:
        for ou_data in ou_datas:
            ou_codes.append(ou_data["short_code"])

        sql = "select id from iuap_apdoc_basedoc.org_orgs where enable = 1 and code in ({})"
        rows = database.fetch_all(sql.format(','.join(["'%s'" % item for item in ou_codes])))
        cust_ou_ids= []
        for cust_ou_id in [row[0] for row in rows]:
            cust_ou_ids.append(cust_ou_id)

    data = []
    insert_cust = {}
    insert_cust["merchantId"] = cust_id
    insert_cust["orgIds"] = cust_ou_ids
    insert_cust["createOrgId"] = '666666'

    data.append(insert_cust)

    # 调用API接口执行分配
    url = "/yonbip/digitalModel/merchant/batchDo"
    api_call = ApiCall()
    body = {}
    body["data"] = data
    print(body)
    hit_nums = api_call.call_api(url=url, payload=body)
    print(hit_nums)

# 已知客户数据，分配适用范围
def customer_adapter_know_cust(customer_data):
    # 数据库连接
    database = MySqlSSH()

    cust0 = customer_data["cust"][0]
    # 客户基础信息
    cust_base = cust0["customer"]
    # 客户编码
    insert_cust_code = cust_base["account_number"]
    # 客户id
    sql = "select id from iuap_apdoc_coredoc.merchant where cCode = '{}'".format(insert_cust_code)
    cust_rows = database.fetch_all(sql)
    if not cust_rows:
        return
    cust_id = [row[0] for row in cust_rows][0]

    # 客户往来公司（适用范围）
    ou_datas = cust0["site"]
    ou_codes = []
    if ou_datas:
        for ou_data in ou_datas:
            ou_codes.append(ou_data["short_code"])

        sql = "select id from iuap_apdoc_basedoc.org_orgs where enable = 1 and code in ({})"
        rows = database.fetch_all(sql.format(','.join(["'%s'" % item for item in ou_codes])))
        cust_ou_ids= []
        for cust_ou_id in [row[0] for row in rows]:
            cust_ou_ids.append(cust_ou_id)

        data = []
        insert_cust = {}
        insert_cust["merchantId"] = cust_id
        insert_cust["orgIds"] = cust_ou_ids
        insert_cust["createOrgId"] = '666666'

        data.append(insert_cust)

        # 调用API接口执行分配
        url = "/yonbip/digitalModel/merchant/batchDo"
        api_call = ApiCall()
        body = {}
        body["data"] = data
        print(body)
        hit_nums = api_call.call_api(url=url, payload=body)
        print(hit_nums)

    database.close()

def customer_adapter_from_file(cust_list=None):
    database = MySqlSSH()
    if cust_list is None:
        cust_list = read_json_to_list('../files/customer.json')
    for cust in cust_list:
        # 客户基础信息
        cust_base = cust["customer"]
        # 客户编码
        insert_cust_code = cust_base["account_number"]
        # 客户id
        sql = "select id from iuap_apdoc_coredoc.merchant where cCode = '{}'".format(insert_cust_code)
        cust_rows = database.fetch_all(sql)
        cust_id = [row[0] for row in cust_rows][0]

        # 客户往来公司（适用范围）
        ou_datas = cust["site"]
        ou_codes = []
        for ou_data in ou_datas:
            ou_codes.append(ou_data["short_code"])

        sql = "select id from iuap_apdoc_basedoc.org_orgs where enable = 1 and code in ({})"
        rows = database.fetch_all(sql.format(','.join(["'%s'" % item for item in ou_codes])))
        cust_ou_ids= []
        for cust_ou_id in [row[0] for row in rows]:
            cust_ou_ids.append(cust_ou_id)

        data = []
        insert_cust = {}
        insert_cust["merchantId"] = cust_id
        insert_cust["orgIds"] = cust_ou_ids
        insert_cust["createOrgId"] = '666666'

        data.append(insert_cust)

        # 调用API接口执行分配
        url = "/yonbip/digitalModel/merchant/batchDo"
        api_call = ApiCall()
        body = {}
        body["data"] = data
        print(body)
        hit_nums = api_call.call_api(url=url, payload=body)
        print(hit_nums)

    database.close()


# 按照核算单位分配
def customer_adapter_by_finace(insert_cust_code, fin_codes=None):
    database = MySqlSSH()

    # 查询内部单位（核算主体）
    fin_ids = []
    if fin_codes:  # 根据提供的核算代码查询
        sql = "select fin.id from iuap_apdoc_basedoc.org_fin fin left join iuap_apdoc_basedoc.org_orgs org on fin.code = org.code where fin.enable = 1 and org.enable = 1 and fin.code in ({})" \
            .format(','.join(["'%s'" % item for item in fin_codes]))
    else:  # 查询所有
        sql = "select fin.id from iuap_apdoc_basedoc.org_fin fin left join iuap_apdoc_basedoc.org_orgs org on fin.code = org.code where fin.enable = 1 and org.enable = 1"
    rows = database.fetch_all(sql)
    for fin_id in [row[0] for row in rows]:
        fin_ids.append(fin_id)

    # 客户id
    sql = "select id from iuap_apdoc_coredoc.merchant where cCode = {}"
    cust_rows = database.fetch_all(sql.format(insert_cust_code))
    cust_id = [row[0] for row in cust_rows][0]

    data = []
    insert_cust = {}
    insert_cust["merchantId"] = cust_id
    insert_cust["orgIds"] = fin_ids
    insert_cust["createOrgId"] = '666666'

    # 调用API接口执行分配
    url = "/yonbip/digitalModel/merchant/batchDo"
    api_call = ApiCall()
    body = {}
    body["data"] = data
    print(body)
    hit_nums = api_call.call_api(url=url, payload=body)
    print(hit_nums)

    database.close()

# 查询
def customer_ou(cust_codes):

    for cust_code in cust_codes:
        customer_data = get_customer(cust_code)

        cust0 = customer_data["cust"][0]

        # 客户往来公司（适用范围）
        ou_datas = cust0["site"]
        ou_codes = []
        for ou_data in ou_datas:
            ou_codes.append(ou_data["short_code"])
        print('客户编码【{}】, EBS-OU【{}】'.format(cust_code, ou_codes))

# 批量同步客户
def sync_cust_batch():
    cust_list = read_json_to_list('../files/customer.json')
    deal_list = []
    ou_deal_no = []
    for cust in cust_list:
        if cust.get("site"):
            ou_deal_no.append(cust.get('customer').get('account_number'))
            deal_list.append(cust)
            cust_list.remove(cust)
            data_sync.data_sync(DataSyncCode.customer, deal_list)
            deal_list = []
    customer_adapter_from_file(cust_list)
    print(ou_deal_no)

# 同步客户、分配适用范围
def sync_customer_batch(cust_nos):

    nodata = []
    for cust_no in cust_nos:
        cust = get_customer(cust_no)
        if len(cust['cust']) != 0:
            data_sync.data_sync(DataSyncCode.customer, cust.get('cust'))
            customer_adapter_know_cust(cust)
        else:
            nodata.append(cust_no)
    if len(nodata) != 0:
        print(nodata)


def customer_adapter_worker(start_idx, end_idx):
    global cust_code_arr
    for i in range(start_idx, end_idx):
        # with lock:  # 确保线程安全
        cust_code = cust_code_arr[i]
        deal_arr = []
        deal_arr.append(cust_code)
        customer_adapter_batch(deal_arr)
def customer_adapter_thread():
    threads = []
    array_size = len(cust_code_arr)
    threads_count = 20
    chunk_size = array_size//threads_count  # 每个线程处理的数据块大小

    # 创建并启动线程
    for i in range(threads_count):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i != threads_count - 1 else array_size
        t = threading.Thread(
            target=customer_adapter_worker,
            args=(start, end)
        )
        threads.append(t)
        t.start()

    # 等待所有线程完成
    for t in threads:
        t.join()


if __name__ == '__main__':
    # get_customer("C59025604")
    # print(json.dumps(get_customer("C70680088")))
    # customer_ou(['100066'])
    # customer_adapter_from_file()
    # customer_adapter_batch()
    # customer_adapter_thread()
    sync_customer_batch(['C00306702'])






