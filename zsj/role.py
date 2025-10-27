# 批量修改员工角色的组织权限
import json

import requests

from util.excel_utils import OperationXlsx
from util.mysql_ssh_utils import MySqlSSH

yht_access_token = 'bttRm9FeVlrd08vL1hHWXA4My9YaXpsaGp2bW1va05BVlpYbnlSNCtmWmVFcDF5UDlaL3VqL2o4VGY0ZHZpR1FrQV9fZnNzY2JpcC5jaGluYWdhc2hvbGRpbmdzLmNvbQ..__3f0ae99b806daf00524db4b9cf490e92_1755218080760TGTGdccore1iuap-apcom-workbenchf4f63618YT'
def update_emp_role_org(role_code):

    db = MySqlSSH()

    excel = OperationXlsx("../files/role/" + role_code + ".xlsx")
    keys = ["user_code", "del_org_name"]
    # 读取文件获取员工信息
    file_read_data_objs = excel.read_excel_to_obj(4, keys)

    user_del_orgs_dict = {}
    user_list = []
    for read_data in file_read_data_objs:
        user_list.append(read_data.user_code)
    for user in user_list:
        user_del_orgs_dict[user] = []

    for read_data in file_read_data_objs:
        user_del_orgs = user_del_orgs_dict[read_data.user_code]
        if read_data.del_org_name:
            user_del_orgs.append(read_data.del_org_name)

    print(user_del_orgs_dict)

    # 按用户操作
    for user_code in user_del_orgs_dict.keys():
        current_user_del_orgs = user_del_orgs_dict[user_code]

        body = {}
        user_roles = []
        # 根据角色查询角色下用户
        sql = ("select role_id, yhtuser_id, user_id, role_snowflake_id from iuap_apcom_auth.user_role where role_code = '{}' and yhtuser_id = (select id from iuap_apcom_auth.ba_user where code = '{}')"
               .format(role_code, user_code))
        user_rolw_rows = db.fetch_all(sql)
        for row in user_rolw_rows:
            user_role = {}
            user_role["roleId"] = row[0]
            user_role["yhtUserId"] = row[1]
            user_role["yxyUserId"] = row[2]
            user_role["roleSnowflakeId"] = row[3]
            user_roles.append(user_role)
        body["userRoles"] = user_roles

        body["userRoles"] = user_roles
        del_org_ids = []
        org_sql = "select id from iuap_apdoc_basedoc.org_orgs where name in ({})".format(','.join(["'%s'" % item for item in current_user_del_orgs]))
        rows = db.fetch_all(org_sql)
        for org_id in [row[0] for row in rows]:
            del_org_ids.append(org_id)

        resources = []
        # 拼装要删除的组织权限，del中是id
        org_unit_del = {}
        org_unit_del["del"] = del_org_ids
        org_unit_del["resourceFunction"] = "orgunit"
        org_unit_del["resourcetypecode"] = "orgdept"
        resources.append(org_unit_del)

        org_fin_del = {}
        org_fin_del["del"] = del_org_ids
        org_fin_del["resourceFunction"] = "financeorg"
        org_fin_del["resourcetypecode"] = "orgdept"
        resources.append(org_fin_del)

        body["resources"] = resources
        body["delRuleCodes"] = []
        print(json.dumps(body))

        payload = json.dumps(body)

        # 调用页面接口处理数据
        # url = 'https://fsscbip.chinagasholdings.com/mdf-node/uniform/serviceIsolate/delOrgAuthsByUserRoleAndRes?serviceCode=u8c_GZTACT020&terminalType=1&locale=zh_CN&sbillno=sys_authRole'
        url = 'https://fsscbip.chinagasholdings.com/mdf-node/uniform/serviceIsolate/delOrgAuthsByUserRoleAndRes?serviceCode=u8c_GZTACT020&terminalType=1&locale=zh_CN&sbillno=sys_authority'

        headers = {
            'domain-key': 'u8c-auth',
            'yht_access_token': yht_access_token,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        # paramData = json.loads(response.text)
        print(response.text)

    return None

if __name__ == '__main__':
    update_emp_role_org('ZR0053')