# 消除待办
import json

import requests

from util.api_call import ApiCall
from util.mysql_ssh_utils import MySqlSSH
from zsj.common import get_soa_auth

yht_access_token = 'bttOUJ2SHRiYXNTSXRtK2xCTlFwQ0VHVUV5VUh6RTlsdlFXYmI4ZHVzbjF1dFVnWXpPUHZaZWlQSmZoQ3BZbEk2U19fZnNzY2JpcC5jaGluYWdhc2hvbGRpbmdzLmNvbQ..__3f0ae99b806daf00524db4b9cf490e92_1743046237899TGTGdccore1iuap-apcom-workbenchea3dafefYT'

# 删除待办
def delete_todo(delete_key):
    # 查询待办
    url = 'https://fsscbip.chinagasholdings.com/iuap-apcom-messagecenter/todocenter/rest/client/web/query/items/list'
    body_data = json.dumps({
      "pageNo": 1,
      "pageSize": 20,
      "createStartTs": "",
      "createEndTs": "",
      "itemStatus": "todo",
      "language": "zh_CN",
      "fieldKeywords": [],
      "sortFiled": "createTsLong",
      "sortType": "desc"
    })
    headers = {
        'yht_access_token': yht_access_token,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=body_data)
    paramData = json.loads(response.text).get('list')

    todo_dict = {}
    todo_object_list = []
    for todo in paramData:
        todo_object = {}
        todo_object['srcMsgId'] = todo['srcMsgId']
        todo_object['businessKey'] = todo['businessKey']
        todo_object['appId'] = todo['appId']
        todo_object['content'] = todo['content']
        todo_object['title'] = todo['title']
        todo_object_list.append(todo_object)
        todo_dict['content'] = todo_object

    print(todo_object_list)

    # 删除BIP的待办
    api_call = ApiCall()
    # 调用内置API接口
    sync_url = '/yonbip/uspace/rest/openapi/idempotent/todo/push/revocation'
    for todo_delete in todo_object_list:
        if delete_key in todo_delete['title']: # 按照标题处理
        # if delete_key in todo_delete['content']: # 按照content处理
            src_msg_id = todo_delete['srcMsgId']
            business_key = todo_delete['businessKey']
            appId = todo_delete['appId']
            body = {
                "srcMsgId": src_msg_id,
                "businessKey": business_key,
                "appId": appId
            }
            result = api_call.call_api(url=sync_url, payload=body)
            if (json.loads(result))['code'] == '200':
                # 删除OA待办
                delete_oa_todo(business_key)
    # return paramData

# 删除OA待办
def delete_oa_todo(business_key):
    # business_key查询：select business_key from zhongran_db.zr_dingtalk_message where receiver='{user_code}' and cancel_response is null
    db = MySqlSSH()
    sql = "select concat(business_key, receiver, resendable) from zhongran_db.zr_dingtalk_message zdm where business_key = '{}'"
    db_result = db.fetch_all(sql.format(business_key))
    fMessageId = [row[0] for row in db_result][0]
    oa_delete_url = 'http://172.22.0.188/ntd-manage/restapi/cancelMsgBatch'
    req_data = json.dumps([{
        "fMessageId": fMessageId,
        "fSysType": "CWGX_SYS"
    }])
    headers = {
        'yht_access_token': yht_access_token,
        'Content-Type': 'application/json'
    }
    response = requests.post(oa_delete_url, json=json.loads(req_data), headers=headers, auth=get_soa_auth())
    print(response.text)

    db.close()


if __name__ == '__main__':
    delete_todo('对账结果查询')
    # delete_oa_todo('e3af982c-f355-11ef-ad62-060aa7890d6d')
