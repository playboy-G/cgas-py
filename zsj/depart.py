import requests
import json

from requests.auth import HTTPBasicAuth

from util.api_call import ApiCall
from util.base64utils import Base64Utils
from util.excel_utils import OperationXlsx
from util.mysql_ssh_utils import MySqlSSH


# 查询MDM组织机构,dept_id传公司级的id，查询公司下所有
def get_depart(dept_id):
    query_url = 'http://soa.chinagasholdings.com:7011/services/2F05002000001'
    username = 'OSB_PRD_BIP'
    password = 'BipPrdq6mx#42'
    auth = HTTPBasicAuth(username, password)

    biz_data_first = json.dumps({
        "applicationCode": "ERP",
        "ifaceCode": "ZZJG",
        "deptId": dept_id,  # 所属组织机构
        "parentDepId": "", # 父级组织机构
        "depType": "", # 机构类型
        "batch": "", # 批次
        "batchHistory": "", # 批次历史
        "startTime": "2000/01/01 00:00:00",
        "endTime": "2025/12/31 23:59:59",
        "pageNumber": 0, # 页数
        "pageSize": 1
    })
    base64_data = Base64Utils.base64_encode(biz_data_first)

    req_data = json.dumps(
        {
            "applicationCode": "ERP",
            "ifaceCode": "ZZJG",
            "auth": "",
            "batch": "",
            "requestData": base64_data,
            "requestId": ""
        }
    )
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'User-Agent':'PostmanRuntime/7.42.0'
    }

    fist_response = requests.post(query_url, json=json.loads(req_data), headers=headers, auth=auth)
    basic_back_data = json.loads(Base64Utils.base64_decode(json.loads(fist_response.text)["data"]))

    # 首次查询的批次号batch
    batch = basic_back_data["batch"]
    # 首次查询的批次号历史batchHistory
    batchHistory = basic_back_data["batchHistory"]
    # 查询总数
    totalCount = basic_back_data["totalCount"]

    loop_biz_data = {}
    loop_biz_data["applicationCode"] = "ERP"
    loop_biz_data["ifaceCode"] = "ZZJG"
    loop_biz_data["deptId"] = dept_id
    loop_biz_data["parentDepId"] = ""
    loop_biz_data["depType"] = ""
    loop_biz_data["batch"] = batch
    loop_biz_data["batchHistory"] = batchHistory
    loop_biz_data["startTime"] = "2000/01/01 00:00:00"
    loop_biz_data["endTime"] = "2025/12/31 23:59:59"
    loop_biz_data["pageSize"] = 50

    hit_depart = []
    max_page = totalCount//50 + 1 if totalCount%50 > 0 else totalCount//50
    for page in range(0, max_page):
        loop_biz_data["pageNumber"] = page
        # 业务参数，需要base64编码
        loop_biz_req = json.dumps(loop_biz_data)
        print(loop_biz_req)
        # 接口请求参数
        loop_req = json.dumps({
            "applicationCode": "ERP",
            "ifaceCode": "ZZJG",
            "auth": "",
            "batch": batch,
            "batchHistory": batchHistory,
            "requestData": Base64Utils.base64_encode(loop_biz_req),
            "requestId": ""
        })
        loop_response = requests.post(query_url, json=json.loads(loop_req), headers=headers, auth=auth)
        loop_biz_resp = json.loads(Base64Utils.base64_decode(json.loads(loop_response.text)["data"]))
        depinfo_all = loop_biz_resp["depInfoList"]
        if not dept_id or dept_id.isspace(): # dept_id为空
            hit_depart.extend(depinfo_all)
        else:
            for depart in depinfo_all:
                if dept_id == depart["deptId"] or dept_id == depart["cgDeptParent"]:
                    hit_depart.append(depart)

    print(json.dumps(hit_depart))


# 更新部门信息（部门负责人，分管领导、成本中心）
def update_depart_base(file_path):
    excel = OperationXlsx(file_path)
    database = MySqlSSH()
    api_call = ApiCall()


    dept_detail_url = '/yonbip/digitalModel/admindept/detail'

    keys = ["org_name","dept_name","dept_code","dept_charge_name","dept_charge_code","dept_manger_name","dept_manger_code","cost_center_name","cost_center_code","dept_nature"]
    # 读取文件获取部门信息，第二行开始为数据行
    file_read_data_objs = excel.read_excel_to_obj(2, keys)
    for depart_base in file_read_data_objs:
        # 查询部门id
        detail_sql = "select id from iuap_apdoc_basedoc.org_admin where code = '{}' and dr = 0"
        rows = database.fetch_all(detail_sql.format(depart_base.dept_code))
        dept_id = [row[0] for row in rows][0]
        # 调用API获取部门详情
        params = {'id': dept_id}
        response = api_call.call_api_get(dept_detail_url, params)
        print(response)

    # 部门批量保存
    save_batch_url = '/yonbip/digitalModel/integrationApi/dept/deptBatchSave'



    database.close()
    return None


if __name__ == '__main__':
    get_depart("201988")
    # update_depart_base('../files/depart.xlsx')





