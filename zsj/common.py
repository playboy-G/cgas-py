# 获取内部公司编码的主键id, 可读取文件; org_type  1-内部公司  2-供应商
import json

from requests.auth import HTTPBasicAuth

from util.constants import Constants
from util.excel_utils import OperationXlsx
from util.mysql_ssh_utils import MySqlSSH

# BIP调用SOA的用户签名
def get_soa_auth():
    return HTTPBasicAuth(Constants.soa_username, Constants.soa_password)

# 读取寄送文件到列表
def read_json_to_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
        return list(json_data)

# 根据组织编码查询组织id
def get_org_id_dict(org_codes, org_type, file_path=None, start_row=0):
    db = MySqlSSH()

    if file_path is None:
        org_codes = org_codes
    else:
        # 提供模板，第一列作为公司代码
        read_file = OperationXlsx(file_path)
        org_codes = read_file.get_col_values_by_id(0)[start_row:]

    sql = None
    if org_type == 1: # 内部公司
        sql = "select id, code from iuap_apdoc_basedoc.org_orgs " \
              "where enable = 1 and  name in (select name from iuap_apdoc_basedoc.org_orgs where code in ({}))"
    elif org_type == 2: # 供应商
        sql = "select id, code from iuap_apdoc_coredoc.aa_vendor " \
              "where name in (select name from iuap_apdoc_coredoc.aa_vendor where code in ({}))"
    rows = db.fetch_all(sql.format(','.join(["'%s'" % item for item in org_codes])))
    results_dict = {}
    for row in rows:
        results_dict[row[1]] = row[0]

    db.close()

    return results_dict

# 根据组织名称查询组织id tax_type: 1-核算主体 2-行政主体
def get_org_id_by_name(org_names, tax_type):
    db = MySqlSSH()

    sql = "select name, code, id from iuap_apdoc_basedoc.org_orgs where enable = 1 and name in ({}) and {}"\
        .format(','.join(["'%s'" % item for item in org_names]),
                "taxpayertype = 1" if tax_type == 1 else "taxpayertype is null")
    rows = db.fetch_all(sql)
    results_dict = {}
    for row in rows:
        results_dict[row[0]] = row[2]

    db.close()

    return results_dict


# 根据部门编码查询部门id
def get_dept_id_by_code(dept_codes):
    db = MySqlSSH()

    sql = "select code, id, name from iuap_apdoc_basedoc.org_admin where enable = 1 and code in ({})" \
        .format(','.join(["'%s'" % item for item in dept_codes]))
    rows = db.fetch_all(sql)
    results_dict = {}
    for row in rows:
        results_dict[row[0]] = row[1]

    db.close()

    return results_dict

# 获取职务ID信息
def get_duty_id_dict():
    db = MySqlSSH()

    sql = "select name, id from iuap_apdoc_basedoc.bd_duty"
    rows = db.fetch_all(sql)
    results_dict = {}
    for row in rows:
        results_dict[row[0]] = row[1]

    db.close()

    return results_dict


if __name__ == '__main__':
    get_duty_id_dict()
















