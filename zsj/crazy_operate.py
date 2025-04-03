# 消除待办
import json

import requests

from util.api_call import ApiCall
from util.mysql_ssh_utils import MySqlSSH
from zsj.common import get_soa_auth

yht_access_token = 'bttUWY0cC8yM29yY2VMd21BdzdYS0hUbU51R0ZYQzR0T3dDTlBoZlJVZFNlY054emtOOFV1SGlKSURmNWVlU1FIVF9fZnNzY2JpcC5jaGluYWdhc2hvbGRpbmdzLmNvbQ..__3f0ae99b806daf00524db4b9cf490e92_1743578553930TGTGdccore1iuap-apcom-workbench363e7669YT'

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

#系统问题导致收款单卡在审批中的处理方案
def fault_unsubmit_rec(receive_codes):
    database = MySqlSSH()
    api_call = ApiCall()

    # 05f6c7bd181e60ea15d6a0ed575abd09b8db8e83
    yht_access_token = 'bttK2pLNXZRV3F5NTlVYnI0RUd6OHFKK0ZyQWNKUkZNWFFLMHc1MHY5cXR1RzRDT21jWkplWmZyVytJMUhWajRGOV9fZnNzY2JpcC5jaGluYWdhc2hvbGRpbmdzLmNvbQ..__3f0ae99b806daf00524db4b9cf490e92_1743563337384TGTGdccore1iuap-apcom-workbenched5a182dYT'
    sql_base = "select id from fiearapbill.ar_collection_h where bill_code = '{}'"
    del_sql_base = "select id_ from iuap_apcom_workflow.act_hi_procinst where business_key_ = '{}'"
    for receive_code in receive_codes:
        sql = sql_base.format(receive_code)
        rec_id_rows = database.fetch_all(sql)
        if rec_id_rows:
            rec_id = [row[0] for row in rec_id_rows][0]
            business_key = 'collection_' + rec_id
            del_sql = del_sql_base.format(business_key)
            delete_key_rows = database.fetch_all(del_sql)
            delete_key = [row[0] for row in delete_key_rows][0]
            withall = 'https://fsscbip.chinagasholdings.com/iuap-apcom-workflownew/ubpm-web-rest/service/runtime/ext/process-instances/' + delete_key + '/false/withall'
            print(withall)
            headers = {
                "sign": "05f6c7bd181e60ea15d6a0ed575abd09b8db8e83",
                'yht_access_token': yht_access_token,
                'Content-Type': 'application/json;charset=UTF-8',
                'source': 'yonbip-fi-earapbill',
                'tenant': 'npuaqm6k'
            }
            result = api_call.call_api_delete(url=withall, headers=headers, data=None)
            if result:
                unsubmit_url = 'https://fsscbip.chinagasholdings.com/mdf-node/uniform/bill/unsubmit?cmdname=cmdUnsubmit&businessActName=收款单-撤回&terminalType=1&busiObj=collection&serviceCode=ear_bill_collection&sbillno=collectionList'
                data = {
                    'id': rec_id,
                    'code': receive_code
                }
                headers = {
                    'Content-Type': 'application/json',
                    'domain-key': 'yonbip-fi-earapbill',
                    'yht_access_token': yht_access_token
                }
                payload = {
                    "billnum": "collection",
                    "data": data
                }
                repsonse = api_call.http_post_headers(unsubmit_url, headers, payload=payload)
                print(repsonse)
    database.close()


if __name__ == '__main__':
    delete_todo('OARar250331275775')
    # delete_oa_todo('e3af982c-f355-11ef-ad62-060aa7890d6d')
    #fault_unsubmit_rec(['RECar250331578628', 'RECar250331578594', 'RECar250331578590'])
