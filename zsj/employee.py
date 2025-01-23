import datetime
import json
import requests
from colorama import Fore, Back, Style
from requests.auth import HTTPBasicAuth

from util.api_call import ApiCall
from util.base64utils import Base64Utils
from util.excel_utils import OperationXlsx
from util.mysql_ssh_utils import MySqlSSH
from zsj import common


# 获取MDM人员信息
def get_mdm_staff(emp_id):
    # MDM 请求地址
    url = "http://soa.chinagasholdings.com:7011/services/2F05002000001"
    username = 'OSB_PRD_BIP'
    password = 'BipPrdq6mx#42'
    auth = HTTPBasicAuth(username, password)

    ryxx_json = {
        "batch": "",
        "batchHistory": "",
        "applicationCode": "ERP",
        "totalCount": 0,
        "startTime": "2000-06-06 00:00:00",
        "endTime": "2025-12-31 00:00:00",
        "pageNumber": 0,
        # "deptId":"132006",
        "empId": emp_id,
        "pageSize": 50,
        "ifaceCode": "RYXX"
    }
    # json.dumps转换成json对象
    ryxx_string = json.dumps(ryxx_json)
    encrypted_data = Base64Utils.base64_encode(ryxx_string)
    qqmdmryxx_json = {
        "applicationCode": "ERP",
        "auth": "",
        "batch": "",
        "ifaceCode": "RYXX",
        "requestData": encrypted_data,
        "requestId": ""
    }

    headers = {
        'Content-Type': 'application/json',
        'User-Agent':'PostmanRuntime/7.42.0'
    }
    print('第一次请求的参数：', json.dumps(qqmdmryxx_json))
    response = requests.request("POST", url, headers=headers, data=json.dumps(qqmdmryxx_json), auth=auth)
    responseData = json.loads(response.text)
    if "data" in responseData:
        resData = json.loads(Base64Utils.base64_decode(responseData["data"]))
        print('第一次返回结果：', json.dumps(resData))
        if "batch" in resData:
            batch = resData['batch']
        if "batchHistory" in resData:
            batchHistory = resData['batchHistory']
        if len(batch) == 0 or len(batchHistory) == 0:
            print("空数据没必要继续请求！")
        else:
            # for i in range(1, 11):
            ryxx_string = json.loads(ryxx_string)
            ryxx_string['batch'] = batch
            ryxx_string['batchHistory'] = batchHistory
            ryxx_string
            json_str = json.dumps(ryxx_string)
            encrypted_data = Base64Utils.base64_encode(json_str)
            qqmdmryxx_json = {
                "applicationCode": "ERP",
                "auth": "",
                "batch": "",
                "ifaceCode": "RYXX",
                "requestData": encrypted_data,
                "requestId": ""
            }
            print("第二次请求参数", json.dumps(qqmdmryxx_json))
            response = requests.request("POST", url, headers=headers, data=json.dumps(qqmdmryxx_json), auth=auth)
            responseData = json.loads(response.text)
            if "data" in responseData:
                resData = json.loads(Base64Utils.base64_decode(responseData["data"]))
            else:
                print("第二次请求数据,返回数据没有data")

            print("人员查询结果：{}".format(json.dumps(resData["custMasterDataIntfList"])))
            return resData["custMasterDataIntfList"]
    else:
        print("返回数据没有data")


# 获取MDM人员任职信息
def get_mdm_staff_job(startDate, endDate, pageNumber, empId):
    ryxx_json = {"batch": "", "batchHistory": "", "applicationCode": "ERP", "totalCount": 0, "startTime": startDate,
                 "endTime": endDate, "pageNumber": pageNumber, "pageSize": 50, "ifaceCode": "RYZZGX", "empId": empId}
    # json.dumps转换成json对象
    ryxx_string = json.dumps(ryxx_json)
    print('请求的参数：', ryxx_string)
    encrypted_data = Base64Utils.base64_encode(ryxx_string)
    qqmdmryxx_json = {
        "applicationCode": "ERP",
        "auth": "",
        "batch": "",
        "ifaceCode": "RYZZGX",
        "requestData": encrypted_data,
        "requestId": ""
    }
    # MDM 请求地址
    # url = "http://soa.chinagasholdings.com:7011/services/2F01502000001"
    url = "http://soa.chinagasholdings.com:7011/services/2F05002000001"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic T1NCX1BSRF9CSVA6QmlwUHJkcTZteCM0Mg==',
        'User-Agent':'PostmanRuntime/7.42.0'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(qqmdmryxx_json))
    responseData = json.loads(response.text)
    if "data" in responseData:
        resData = json.loads(Base64Utils.base64_decode(responseData["data"]))
        print('第一次请求的data解密的数据' + Fore.BLUE, resData)
        if "batch" in resData:
            batch = resData['batch']
        if "batchHistory" in resData:
            batchHistory = resData['batchHistory']
        if len(batch) == 0 or len(batchHistory) == 0:
            print("空数据没必要继续请求！")
        else:
            ryxx_string = json.loads(ryxx_string)
            ryxx_string['batch'] = batch
            ryxx_string['batchHistory'] = batchHistory
            json_str = json.dumps(ryxx_string)
            print("第二次请求的入参:" + Fore.BLUE, json_str)
            encrypted_data = Base64Utils.base64_encode(json_str)
            print("第二次请求的加密数据:" + encrypted_data)
            qqmdmryxx_json = {
                "applicationCode": "ERP",
                "auth": "",
                "batch": "",
                "ifaceCode": "RYZZGX",
                "requestData": encrypted_data,
                "requestId": ""
            }
            response = requests.request("POST", url, headers=headers, data=json.dumps(qqmdmryxx_json))
            responseData = json.loads(response.text)
            if "data" in responseData:
                resData = json.loads(Base64Utils.base64_decode(responseData["data"]))
                result = json.dumps(resData, ensure_ascii=False)
                fp = open('任职数据.json', 'w')
                print(json.dumps(resData, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')),
                      file=fp)
                print('第二次请求数据入参：' + json.dumps(qqmdmryxx_json))
                print('第二次请求数据响应：' + Fore.RED, result)
            else:
                print("第二次请求数据,返回数据没有data")
    else:
        print("返回数据没有data")


# API接口获取员工详情
def get_employee_by_api(employee_codes, employee_id=None):
    api_call = ApiCall()

    url = '/yonbip/digitalModel/staff/detail'
    employees = []
    for employee_code in employee_codes:
        params = {
            "id": employee_id,
            "code": employee_code
        }
        hits = json.loads(api_call.call_api_get(url, params))
        if hits["code"] == '200':
            employees.append(hits["data"])

    return employees


# 根据API接口导入员工兼职
def put_part_time_by_file(file_path):
    # 读取文件，路径改成传参数
    excel = OperationXlsx(file_path)

    # 查询BIP员工信息
    employee_codes = list(set(excel.get_col_values_by_id(2, 0)))
    employee_effect_codes = []
    for employee_code in employee_codes:
        if employee_code is not None:
            employee_effect_codes.append(employee_code)
    employees = get_employee_by_api(employee_effect_codes)

    # 查询所有公司名称对应的行政组织id
    org_names = list(set(excel.get_col_values_by_id(2, 2)))
    org_effect_names = []
    for org_name in org_names:
        if org_name is not None:
            org_effect_names.append(org_name)
    org_id_dict = common.get_org_id_by_name(org_effect_names, 2)

    # 查询所有部门编码对应的id
    dept_codes = list(set(excel.get_col_values_by_id(2, 4)))
    dept_effect_codes = []
    for dept_code in dept_codes:
        if dept_code is not None:
            dept_effect_codes.append(dept_code)
    dept_id_dict = common.get_dept_id_by_code(dept_effect_codes)

    # 获取职务id信息
    # duty_dict = common.get_duty_id_dict()

    keys = ["emp_code", "emp_name", "pt_org_name", "pt_dept_name", "pt_dept_code", "duty", "email", "phone", "status"]
    # 读取文件获取员工兼职信息
    file_read_data_objs = excel.read_excel_to_obj(3, keys)
    print(file_read_data_objs)

    # 根据员工编码归集新增的兼职
    emp_pt_dict = {}
    # 按行和员工编码，将同一员工的兼职进行归集
    for data in file_read_data_objs:
        # data为每一行数据对象
        if data.emp_code in emp_pt_dict:
            per_emp_pts = emp_pt_dict.get(data.emp_code)
        else:
            per_emp_pts = []
        per_emp_pt = {}
        per_emp_pt["org_id"] = org_id_dict[data.pt_org_name]
        per_emp_pt["dept_id"] = dept_id_dict[data.pt_dept_code]
        # per_emp_pt["job_id"] = duty_dict[data.duty]
        per_emp_pt["begindate"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        per_emp_pt["_status"] = "insert"
        per_emp_pts.append(per_emp_pt)
        emp_pt_dict[data.emp_code] = per_emp_pts
    print(emp_pt_dict)

    # 处理接口请求参数
    body = {}
    req_date = []
    for employee in employees:
        try:
            emp_update = {}
            emp_update["id"] = employee["id"]
            emp_update["code"] = employee["code"]
            emp_update["name"] = employee["name"]
            emp_update["_status"] = "Update"
            main_jobs = employee["mainJobList"]
            for main_job in main_jobs:
                main_job["_status"] = "Update"
            # 主要任职，目前只有一条，原数据取回
            emp_update["mainJobList"] = main_jobs

            # 已经存在的兼职公司id和部门id组合
            old_pt_org_dept_ids = []
            old_pt_job_id_dept_dict = {}
            old_pt_jobs = employee["ptJobList"] if "ptJobList" in employee else []
            for old_pt_job in old_pt_jobs:
                old_pt_org_dept_id = "{}#{}".format(old_pt_job["org_id"], old_pt_job["dept_id"])
                old_pt_org_dept_ids.append(old_pt_org_dept_id)
                old_pt_job_id_dept_dict[old_pt_job["dept_id"]] = old_pt_job["id"]

            # 新兼职，可多个
            pt_jobs = emp_pt_dict[employee["code"]]
            for pt_job in pt_jobs:
                new_pt_org_dept_id = "{}#{}".format(pt_job["org_id"], pt_job["dept_id"])
                # 新加的兼职存在则更新，不存在则新增
                if new_pt_org_dept_id in old_pt_org_dept_ids:
                    pt_job["id"] = old_pt_job_id_dept_dict[pt_job["dept_id"]]
                    pt_job["_status"] = "Update"
                else:
                    pt_job["_status"] = "Insert"
            emp_update["ptJobList"] = pt_jobs

            req_date.append(emp_update)
        except:
            print(employee)
    body["data"] = req_date

    print("员工批量新增请求体：{}".format(body))

    # 调用APi接口
    api_call = ApiCall()
    url = "/yonbip/digitalModel/staff/batchSave"
    hit_nums = api_call.call_api(url=url, payload=body)
    print(hit_nums)




if __name__ == '__main__':
    # get_mdm_staff("10096680")
    get_mdm_staff_job("2000-01-01", "2025-12-31", 0, "10096680")
    # get_employee_by_api("ZSJWH")
    # put_part_time_by_file("../files/pt.xlsx")
