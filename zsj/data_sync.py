import json

from util.api_call import ApiCall
from util.constants import Constants, DataSyncCode
import zsj.common as common
import zsj.customer as customer
from util.mysql_ssh_utils import MySqlSSH
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
def sync_project(flex_value=None, date_from=None, date_to=None):
    ebs_projects = get_coa(6, flex_value=flex_value, date_from=date_from, date_to=date_to)
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

def sync_projec_batcht(flex_values):
    for flex_value in flex_values:
        sync_project(flex_value=flex_value, date_from='', date_to='')


if __name__ == '__main__':
    # 资产卡片
    # data_sync(DataSyncCode.asset, get_assets(asset_id='10446872', book_type_code='CG_FA_340002'))
    # 项目
    # sync_project(flex_value='10004622GG1226',date_from='', date_to='')
    # sync_projec_batcht(['45009825GB0001','45009825HA0001'])
    # 段值
    data_sync(DataSyncCode.coa8, get_coa(1, '110033', '',''))
    # data_sync(DataSyncCode.accountEntry, [{"flex_value":"440143"}])

    # 物料 data查询MDM
    # data_sync(DataSyncCode.material, data)
    # 物料分配组织 data查询MDM
    # data_sync(DataSyncCode.materialCodeAlloca, data)








