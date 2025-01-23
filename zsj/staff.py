import requests
import json
import hashlib
import hmac
import time
from urllib.parse import quote
import base64

# 同步某一个员工
mdm_staff_url = 'https://fsscbip.chinagasholdings.com/zhongran-be/mdm-itemclass'
host = 'https://fsscbip.chinagasholdings.com'
app_key = 'af9b69ef564f48349f30fec248736778'
app_secret = '510d020448d794457bd05d4650e54af5929bf418'


def call_api(url, payload):
    api = '{}{}?access_token={}&tenantId=npuaqm6k'.format(host, url, access_token())
    return http_post(api, payload=payload)


def http_post(url, payload=None, headers=None):
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    json_payload = ""
    if payload is not None:
        json_payload = json.dumps(payload)
    response = requests.post(url, data=json_payload, headers=headers)
    print('接口: {}, 返回状态码: {}响应报文为: {}'.format(url, response.status_code, response.text))
    return response.text


def access_token():
    endpoint = '/iuap-api-auth/open-auth/selfAppAuth/getAccessToken'
    timestamp = int(time.time() * 1000)
    content = 'appKey{}timestamp{}'.format(app_key, timestamp)
    digest = hmac.new(app_secret.encode('utf-8'), content.encode('utf-8'), hashlib.sha256).digest()
    signature = quote(base64.b64encode(digest).decode('utf-8'))
    response = requests.get(
        '{}{}?appKey={}&timestamp={}&signature={}'.format(host, endpoint, app_key, timestamp, signature))
    body = json.loads(response.text)
    if body['code'] == '00000':
        return body['data']['access_token']
    else:
        return ''


# 获取单个员工同步的数据
def get_one_staff(empId):
    payload = json.dumps({
        "startTime": "2000-06-01",
        "endTime": "2030-01-02",
        "pageNumber": "0",
        "pageSize": "50",
        "empId": empId
    })
    headers = {
        'yht_access_token': yht_access_token,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", mdm_staff_url, headers=headers, data=payload)
    paramData = json.loads(response.text)
    try:
        return paramData["custMasterDataIntfList"]
    except Exception as e:
        return ''


def getStaffs(startDate, endDate, batch, batchHistory, pageNumber):
    url = "https://fsscbip.chinagasholdings.com/zhongran-be/mdm-itemclass"
    payload = json.dumps({
        "startTime": startDate,
        "endTime": endDate,
        "batch": batch,
        "batchHistory": batchHistory,
        "pageNumber": pageNumber
    })
    headers = {
        'yht_access_token': yht_access_token,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    paramData = json.loads(response.text)
    return paramData


yht_access_token = "bttZ2d0SnlHVDJBRGxybzdVMytQZE4xNWtoVi80VWx0VzZxQjJoL2ZLeFAybGFOQ2lxaTVMeHBSMDRKWTJlT0p0M19fZnNzY2JpcC5jaGluYWdhc2hvbGRpbmdzLmNvbQ..__3f0ae99b806daf00524db4b9cf490e92_1735784226671TGTGdccore1iuap-apcom-workbenchc5946861YT"
startDate = '2024-04-20'
endDate = '2024-04-21'

if __name__ == '__main__':
    # api = access_token()
    emplIds = [
        10157598
    ]
    for index, item in enumerate(emplIds):
        # for item in range(10154200, 10154298):
        requestData = get_one_staff(item)
        print(f"当前执行在第 {index + 1} 个循环")
        if requestData:
            # for data in requestData:
            #     if 'mobile' in data:
            #         data['mobile'] = data['mobile'].replace(' ', '')
            paramData = {
                "schemeCode": "bipkk_saveitem_bip_saveitem",
                "data": requestData
            }
            print(paramData)
            if (requestData[0]['hrStatus'] == 'A'):
                print(requestData[0]['empId'])
                call_api('/iuap-api-gateway/yonbip/yonlinker/task/syncdata', paramData)
