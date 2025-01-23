import json

from util.api_call import ApiCall
from util.constants import Constants, DataSyncCode
import zsj.common as common
import zsj.customer as customer
from zsj.ebs_base import get_assets, get_coa


# 数据同步基础接口
def data_sync(schemeCode, data):
    request_body = {
        "schemeCode": schemeCode,
        "data": json.dumps(data),
        "async": False,
        "compressEnable": False,
        "dataFormat": "array"
    }

    # 调用内置接口
    sync_url = '/yonbip/yonlinker/task/syncdata'
    api_call = ApiCall()
    hit_nums = api_call.call_api(url=sync_url, payload=request_body)
    print(hit_nums)


# 项目同步
def sync_project(date_from, date_to):
    # ebs_projects = get_coa(6, date_from, date_to)
    ebs_projects = [{
        "ledger_id": "2021",
        "column_name": "CG_COA_PROJECTS",
        "flex_value": "41008223HB0018",
        "parent_flex_value": "",
        "description": "宁陵县臻爱贝比母婴用品店",
        "summary_flag": "N",
        "enabled_flag": "Y",
        "start_date_active": "",
        "end_date_active": "",
        "attribute1": "H1",
        "attribute2": "",
        "cux_attribute": "H1-H3--H4--",
        "cux_attribute_desc": "安装业务-商业户-经营区域内-小微型商业用户",
        "creation_date": "2023-08-19",
        "created_by": "28223",
        "structured_hierarchy_name": "",
        "fa_project_flag": "H1",
        "cash_item": "",
        "hp_flag": "Y",
        "account_flag": "Y",
        "account_type": "",
        "account_type_desc": "",
        "third_ctl_flag": "",
        "adjust_flag": "",
        "category_limit": ""
    }]
    sync_list = []
    for project in ebs_projects:
        sync_data = {}
        sync_data['flex_value'] = project.get('flex_value')
        sync_data['description'] = project.get('description')
        sync_data['orgCode'] = project.get('flex_value')[0:6]
        attribute = {}
        attribute['cux_attribute'] = project.get('cux_attribute')
        attribute['cux_attribute_desc'] = project.get('cux_attribute_desc')
        sync_data['attribute'] = attribute

        sync_list.append(sync_data)

    data_sync(DataSyncCode.project, sync_list)




if __name__ == '__main__':
    # 资产卡片
    data_sync(DataSyncCode.asset, get_assets(date=None, asset_id='10497669', book_type_code='CG_FA_150001'))
    # 供应商
    # data_sync(DataSyncCode.supplier, get_supplier('C71660573').get('lines'))
    # 员工
    # data_sync(DataSyncCode.staff, get_mdm_staff("10158096"))
    # 客户
    # data_sync(DataSyncCode.customer, get_customer("C71824239").get('cust'))
    # 项目
    # sync_project('2023-08-18', '2023-08-21')


