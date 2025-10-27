# 资产查询
import json
from datetime import datetime, timedelta

import requests
from requests.auth import HTTPBasicAuth

from util.base64utils import Base64Utils
from util.constants import Constants
from zsj.common import get_soa_auth


# 资产卡片 asset_id-资产编码 book_type_code-资产账簿编码
def get_assets(date=None, asset_id=None, book_type_code=None):
    auth = get_soa_auth()

    biz_data = None
    if asset_id is not None:
        biz_data = json.dumps({
            "p_asset_id": asset_id,
            "p_book_type_code": book_type_code
        })
    else:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        next_day = date_obj + timedelta(days=1)
        biz_data = json.dumps({
            "p_lu_date_begin": date_obj.strftime('%Y-%m-%d'),
            "p_lu_date_end": next_day.strftime('%Y-%m-%d'),
        })

    base64_data = Base64Utils.base64_encode(biz_data)

    req_data = json.dumps(
        {
            "comm_ws": {
                "@xmlns": "http://xmlns.oracle.com/apps/per/rest/comm_ws/invokeebsws",
                "RESTHeader": {
                    "xmlns": "http://xmlns.oracle.com/apps/per/rest/comm_ws/header",
                    "Org_Id": "0",
                    "NLSLanguage": "SIMPLIFIED CHINESE",
                    "RespApplication": "CUX",
                    "Responsibility": "CG_CUX_WS_RESP",
                    "SecurityGroup": "STANDARD"
                },
                "InputParameters": {
                    "P_IFACE_CODE": "10BIP_ACIA",
                    "P_BATCH_NUMBER": "00100202308100111",
                    "P_REQUEST_DATA": base64_data
                }
            }
        }
    )
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'User-Agent': 'PostmanRuntime/7.42.0'
    }

    asset_data = None
    try:
        response = requests.post(Constants.soa_ebs_url, json=json.loads(req_data), headers=headers, auth=auth)
        if response.status_code == 200:
            print('Request was successful.')
            back_data = json.loads(response.text)
            asset_data = Base64Utils.base64_decode(back_data["OutputParameters"]["X_RESPONSE_DATA"])
        else:
            print('Request failed {}', response.status_code)
    except requests.exceptions.RequestException as e:
        print('error:', e)

    print(asset_data)
    return json.loads(asset_data).get('returnrequest')


# 九段值 SEGMENT取值对照：1-公司段 2-部门段 3-科目段 4-子目段 5-产品段 6-项目端 7-往来段 8-管理维度段 9-备用段
def get_coa(seg_value, flex_value=None, date_from=None, date_to=None):
    biz_data = json.dumps({
        "ledger_name": 'CG_中燃集团账套',                    # 账套名称
        "segment_column":"SEGMENT" + str(seg_value),   # 段名
        "flex_value": flex_value,                      # 段值编码
        "date_from": date_from,                        # 开始时间
        "date_to": date_to,                            # 结束时间
        "rule_flag": "N"
    })

    base64_data = Base64Utils.base64_encode(biz_data)
    req_data = json.dumps({
        # "P_IFACE_CODE": "10GL_COA",
        "P_IFACE_CODE": "10GL_COA_SEG",  #new
        "P_BATCH_NUMBER": "0100202108270602",
        "P_REQUEST_DATA": base64_data
    })
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'User-Agent': 'PostmanRuntime/7.42.0'
    }

    coa_data = None
    try:
        response = requests.post(Constants.soa_ebs_url, json=json.loads(req_data), headers=headers, auth=get_soa_auth())
        if response.status_code == 200:
            print('Request was successful.')
            back_data = json.loads(response.text)
            coa_data = Base64Utils.base64_decode(back_data["OutputParameters"]["X_RESPONSE_DATA"])
        else:
            print('Request failed {}', response.status_code)
    except requests.exceptions.RequestException as e:
        print('error:', e)

    print(coa_data)
    return json.loads(coa_data).get('headers')[0].get('lines')


# 企业银行账户
def get_org_bank(org_code):
    username = 'OSB_PRD_BIP'
    password = 'BipPrdq6mx#42'
    auth = HTTPBasicAuth(username, password)

    # {"ou_code": "公司代码", "Bank_Number": "银行编号", "Bank_Name": "银行名称", "Branch_Number": "分行编号", "Bank_Branch_Name": "分行名称", "Bank_Account_Num": "银行账号", "Bank_Account_Name": "银行账号名称", "date_from": "起始时间", "date_to": "结束时间"}
    biz_data = json.dumps({
        "ou_code": org_code,
        "Bank_Number": "",
        "Bank_Name": "",
        "Branch_Number": "",
        "Bank_Branch_Name": "",
        "Bank_Account_Num": "",
        "Bank_Account_Name": "",
        "date_from": "",
        "date_to": ""
    })
    base64_data = Base64Utils.base64_encode(biz_data)

    req_data = json.dumps({
        "P_IFACE_CODE": "10CE_BANK",
        "P_BATCH_NUMBER": "0100202108270602",
        "P_REQUEST_DATA": base64_data
    })
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'User-Agent': 'PostmanRuntime/7.42.0'
    }

    org_bank_data = None
    try:
        response = requests.post(Constants.soa_ebs_url, json=json.loads(req_data), headers=headers, auth=auth)
        if response.status_code == 200:
            back_data = json.loads(response.text)
            org_bank_data = Base64Utils.base64_decode(back_data["OutputParameters"]["X_RESPONSE_DATA"])
            print(org_bank_data)
            return org_bank_data
        else:
            print('Request failed {}', response.status_code)
    except requests.exceptions.RequestException as e:
        print('An error occurred:', e)

    # return json.loads(org_bank_data)



if __name__ == '__main__':
    # 具体资产编码查
    # get_assets('','10426960', book_type_code='CG_FA_450008')
    # 段值 1-公司段 2-部门段 3-科目段 4-子目段 5-产品段 6-项目端 7-往来段 8-管理维度段 9-备用段
    get_coa(2, flex_value='1000310023', date_from='', date_to='')
    # 企业银行账户
    # get_org_bank('310004')