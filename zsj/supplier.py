import argparse
from concurrent.futures import ThreadPoolExecutor

import requests
import json

from requests.auth import HTTPBasicAuth

from util.api_call import ApiCall
from util.base64utils import Base64Utils
from util.excel_utils import OperationXlsx
from util.mysql_ssh_utils import MySqlSSH
from zsj import common


# 查询供应商
def get_supplier(vendor_no):
    query_url = 'http://soa.chinagasholdings.com:7011/services/F00100000011'
    username = 'OSB_PRD_BIP'
    password = 'BipPrdq6mx#42'
    auth = HTTPBasicAuth(username, password)

    # {"Vendor_Name":"","Ou_Code":"","date_to":"2024-12-31","Vendor_No":"","date_from":"2018-01-01"}
    biz_data = json.dumps({
        "Vendor_No": vendor_no,
        "Vendor_Name": "",
        "Ou_Code": "",
        "date_to": "2025-12-31",
        "date_from": "2018-01-01"
    })
    base64_data = Base64Utils.base64_encode(biz_data)

    req_data = json.dumps(
        {
            "comm_ws": {
                "@xmlns": "http://xmlns.oracle.com/apps/per/rest/comm_ws/invokeebsws",
                "RESTHeader": {
                    "xmlns": "http://xmlns.oracle.com/apps/per/rest/comm_ws/header",
                    "Responsibility": "CG_CUX_WS_RESP",
                    "RespApplication": "CUX",
                    "SecurityGroup": "STANDARD",
                    "NLSLanguage": "SIMPLIFIED CHINESE",
                    "Org_Id": "0"
                },
                "InputParameters": {
                    "P_IFACE_CODE": "10AP_VENDOR",
                    "P_BATCH_NUMBER": "001002018042100011",
                    "P_REQUEST_DATA": base64_data
                }
            }
        }
    )
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'User-Agent':'PostmanRuntime/7.42.0'
    }

    supplier_data = None
    try:
        response = requests.post(query_url, json=json.loads(req_data), headers=headers, auth=auth)
        if response.status_code == 200:
            print('Request was successful.')
            back_data = json.loads(response.text)
            supplier_data = Base64Utils.base64_decode(back_data["OutputParameters"]["X_RESPONSE_DATA"])
            # print(supplier_data)
        else:
            print('Request failed {}', response.status_code)
    except requests.exceptions.RequestException as e:
        print('An error occurred:', e)

    print(supplier_data)
    return json.loads(supplier_data)

# 批量分配适用范围
def supplier_adapter_batch(vendor_codes):
    # 数据库连接
    database = MySqlSSH()

    for vendor_code in vendor_codes:
        supplier_adapter(vendor_code, database)

    database.close()

# 分配适用范围
def supplier_adapter(vendor_code, database):
    supplier_data = get_supplier(vendor_code)

    data_lines = supplier_data["lines"]
    # 去除所有不重复的供应商编码
    vendor_no_list = set()
    for data_line in data_lines:
        vendor_no = data_line["Vendor_No"]
        vendor_no_list.add(vendor_no)

    # 供应商ou归集
    vendor = {}
    vendor_list = []
    vendor_ou_codes = []
    vendor_ou_ids = []
    for vendor_no in vendor_no_list:
        vendor["vendor_no"] = vendor_no
        adapter_codes = []
        for data_line in data_lines:
            if (data_line["Vendor_No"] == vendor_no):
                # 核算组织编码
                ou_code = data_line["Ou_Code"]
                # 查询行政组织代码
                sql = "select id, code from iuap_apdoc_basedoc.org_orgs " \
                      "where enable = 1 and  name = (select name from iuap_apdoc_basedoc.org_orgs where dr = 0 and code='{}')"
                rows = database.fetch_all(sql.format(ou_code))
                if rows:
                    for vendor_ou_code in [row[1] for row in rows]:
                        vendor_ou_codes.append(vendor_ou_code)
                    for vendor_ou_id in [row[0] for row in rows]:
                        vendor_ou_ids.append(vendor_ou_id)
        vendor["vendor_ou_codes"] = vendor_ou_codes
        vendor["vendor_ou_ids"] = list(set(vendor_ou_ids))
        vendor_list.append(vendor)
        print(vendor_list)

    # 遍历供应商，执行适用范围插入操作
    data = []
    for temp_vendor in vendor_list:
        insert_vendor = {}
        vendor_no = temp_vendor["vendor_no"]
        sql = "select id from iuap_apdoc_coredoc.aa_vendor where code = '{}'";
        rows = database.fetch_all(sql.format(vendor_no))
        vendor_id = [row[0] for row in rows][0]
        insert_vendor["vendorId"] = vendor_id
        insert_vendor["orgIds"] = temp_vendor["vendor_ou_ids"]
        data.append(insert_vendor)

    # 调用API接口执行分配
    url = "/yonbip/digitalModel/vendor/addvendorsuitorg"
    api_call = ApiCall()
    body = {}
    body["data"] = data
    print(body)
    hit_nums = api_call.call_api(url=url, payload=body)
    print(hit_nums)


# 读取文件分配组织
def supplier_adapter_by_excel(file_path, sheet_name=None):
    # 数据库连接
    database = MySqlSSH()

    excel_util = OperationXlsx(file_path, sheet_name)
    # names = excel_util.get_col_valuesById(1)
    sheet_rows = excel_util.get_sheet_lines()

    vendor_list = []
    for row_num in range(1, sheet_rows):
        vendor = {}
        data_row = excel_util.get_row_values_by_id(row_num)

        # 公司主体名称
        # org_name = data_row[0]
        # # 查询公司主体id，就是需要分配的适用范围
        # org_sql = "select id from iuap_apdoc_basedoc.org_orgs where enable = 1 and name = '{}'"
        # vendor_ou_ids = []
        # ou_id_rows = database.fetch_all(org_sql.format(org_name))
        # for vendor_ou_id in [row[0] for row in ou_id_rows]:
        #     vendor_ou_ids.append(vendor_ou_id)

        # 供应商名称
        vendor_name = data_row[1]
        # 查询供应商id
        vendor_sql = "select id from iuap_apdoc_coredoc.aa_vendor where code = '{}'"
        vendor_id_rows = database.fetch_all(vendor_sql.format(vendor_name))
        if vendor_id_rows:
            vendor["vendorId"] = [row[0] for row in vendor_id_rows][0]

        # vendor["orgIds"] = vendor_ou_ids
        vendor["orgIds"] = ['1806152589975748676','1808403771298414615']
        vendor_list.append(vendor)

    print(vendor_list)

    body = {}
    body["data"] = vendor_list

    print(body)

    url = "/yonbip/digitalModel/vendor/addvendorsuitorg"
    api_call = ApiCall()
    hit_nums = api_call.call_api(url=url, payload=body)
    print(hit_nums)

    database.close()

# 根据会计主体分配供应商适用范围
def supplier_dapter_by_finance(vendor_codes, fin_codes=None):
    # 数据库连接
    database = MySqlSSH()

    vendor_id_dict = common.get_org_id_dict(vendor_codes, 2)

    vendor_list = []
    for vendor_code in vendor_codes:
        vendor = {}
        fin_ids = []
        if fin_codes: # 根据核算代码查询
            sql = "select fin.id from iuap_apdoc_basedoc.org_fin fin left join iuap_apdoc_basedoc.org_orgs org on fin.code = org.code where fin.enable = 1 and org.enable = 1 and fin.code in ({})"\
                .format(','.join(["'%s'" % item for item in fin_codes]))
        else: # 查询所有
            sql = "select fin.id from iuap_apdoc_basedoc.org_fin fin left join iuap_apdoc_basedoc.org_orgs org on fin.code = org.code where fin.enable = 1 and org.enable = 1"
        rows = database.fetch_all(sql)
        for vendor_ou_id in [row[0] for row in rows]:
            fin_ids.append(vendor_ou_id)

        vendor["vendorId"] = vendor_id_dict.get(vendor_code)
        vendor["orgIds"] = fin_ids
        vendor_list.append(vendor)


    body = {}
    body["data"] = vendor_list
    print(body)

    url = "/yonbip/digitalModel/vendor/addvendorsuitorg"
    api_call = ApiCall()
    hit_nums = api_call.call_api(url=url, payload=body)
    print(hit_nums)

    database.close()

def supplier_adapter_org(vendor_codes):
    # 数据库连接
    database = MySqlSSH()

    vendor_id_dict = common.get_org_id_dict(vendor_codes, 2)

    # 调用API接口执行分配
    url = "/yonbip/digitalModel/vendor/addvendorsuitorg"
    api_call = ApiCall()

    for vendor_code in vendor_codes:
        data = []
        insert_vendor = {}
        insert_vendor["vendorId"] = vendor_id_dict.get(vendor_code)
        insert_vendor["orgIds"] = ['1808404303874359310','1806152967932870704']
        data.append(insert_vendor)
        body = {}
        body["data"] = data

        # 调用API接口执行分配
        print(body)
        hit_nums = api_call.call_api(url=url, payload=body)
        print(hit_nums)

    database.close()

def example(file_name):
    print(file_name)
def supplier_adapter_thread(dir_path):
    file_names = ['AAAAA','BBBBBBB','CCCCCC']
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(example, file_name) for file_name in file_names]


def main(args):
    get_supplier(args.supplier_code)

if __name__ == '__main__':
    # 查询EBS供应商信息
    # get_supplier('S00193735')
    # 查询EBS数据分配组织
    # supplier_adapter_batch(['420163'])
    # 按照供应商明细表分配组织
    # supplier_adapter_by_excel("../files/CUX.xlsx")
    # 查询供应商查询组织id
    # get_org_id_dict(["S00012275"], 2)

    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("supplier_code", type=str, help="supplier_code")
    args = parser.parse_args()
    main(args)


