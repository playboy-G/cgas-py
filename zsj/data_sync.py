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
    # data_sync(DataSyncCode.asset, get_assets(asset_id='10110333', book_type_code='CG_FA_320024'))
    # 供应商
    # data_sync(DataSyncCode.supplier, get_supplier('C71660573').get('lines'))
    # 员工
    # data_sync(DataSyncCode.staff, get_mdm_staff("10158096"))
    # 客户
    # data_sync(DataSyncCode.customer, get_customer("C71824239").get('cust'))
    # 项目
    # sync_project('2023-08-18', '2023-08-21')
    # 段值
    # data_sync(DataSyncCode.coa8, get_coa(8, '2025-03-25', '2025-03-31'))
    # data_sync(DataSyncCode.accountEntry, [{"flex_value":"440143"}])

    # 物料分配组织
    # database = MySqlSSH()
    proCode = ['10055240',
               '10055239',
               '10055238',
               '10055237',
               '10055236',
               '10055234',
               '10033819',
               '10033818',
               '10033817',
               '10055226',
               '10055225',
               '10055224',
               '10055223',
               '10033804',
               '10033914',
               '10033913',
               '10033900',
               '10033891',
               '10033890',
               '10033889',
               '10033888',
               '10033876',
               '10033875',
               '10033874',
               '10033873',
               '10055208',
               '10055200',
               '10034007',
               '10034023',
               '10034006',
               '10034022',
               '10034004',
               '10055211',
               '10055210',
               '10033997',
               '10055209',
               '10033996',
               '10033995',
               '10055208',
               '10033994',
               '10055218',
               '10033814',
               '10034018',
               '10033808',
               '10056751',
               '10033886',
               '10033804',
               '10033876',
               '10033803',
               '10033875',
               '10033802',
               '10033874',
               '10033873',
               '10033910',
               '10033899',
               '10033898',
               '10033923',
               '10033922',
               '10034052',
               '10062702',
               '10012659',
               '10011956',
               '10010814',
               '10010287',
               '10011813',
               '10012661',
               '10062873',
               '10012661',
               '10056809',
               '10011660',
               '10012648',
               '10010146',
               '10012635',
               '10011671',
               '10011677',
               '10012635',
               '10060576',
               '10012637',
               '10012649',
               '10062518',
               '10012639',
               '10050285',
               '10012638',
               '10010510',
               '10012650',
               '10010508',
               '10040048',
               '10042343',
               '10062520',
               '10010145',
               '10057541',
               '10062874',
               '10019328',
               '10062892',
               '10062887',
               '10062890',
               '10010147',
               '10010144',
               '10011905',
               '10026982',
               '10011904',
               '10062889',
               '10062888',
               '10011892',
               '10011909',
               '10062518',
               '10062887',
               '10010139',
               '10010141',
               '10010135',
               '10011810',
               '10011687',
               '10011808',
               '10062886',
               '10011817',
               '10011815',
               '10011811',
               '10054347',
               '10010339',
               '10010511',
               '10010143',
               '10017053',
               '10062885',
               '10062884',
               '10011653',
               '10011674',
               '10011676',
               '10011656',
               '10011678',
               '10010340',
               '10011679',
               '10011658',
               '10050285',
               '10011659',
               '10062515',
               '10017050',
               '10010344',
               '10010343',
               '10062883',
               '10011681',
               '10010148',
               '10011885',
               '10062518',
               '10011887',
               '10010142',
               '10011888',
               '10011890',
               '10011891',
               '10011685',
               '10011682',
               '10010137',
               '10011655',
               '10010061'
               ]
    proCode1 = ['10055200']
    # sql = "select id from iuap_apdoc_coredoc.product where code = '{}'"
    for code in proCode1:
        data = []
        temp = {}
        temp['companyCode'] = '100012'
        # rows = database.fetch_all(sql.format(code))
        # id = [row[0] for row in rows][0]
        temp['id'] = code
        data.append(temp)
        data_sync(DataSyncCode.product, data)
    # database.close()





