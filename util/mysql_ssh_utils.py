import pymysql
from sshtunnel import SSHTunnelForwarder


class MySqlSSH:
    def __init__(self):
        # self.server = SSHTunnelForwarder(
        #     ssh_address_or_host=('172.30.0.28', 22),    # ssh host
        #     ssh_username='bipfssc',      # ssh 账号
        #     ssh_password='BLiz&-Kft73Ps',   # ssh 密码
        #     remote_bind_address=('127.0.0.1', 3306)   # 数据库配置
        # )
        # # 启动隧道服务
        # self.server.start()
        # mysql_config = {
        #     'user': 'oper_dc',
        #     'passwd': 'operzADF2020qwer',
        #     'host': '127.0.0.1',  # 此处必须是是127.0.0.1
        #     'port': self.server.local_bind_port,
        #     # 'db': 'ph_data_bossjob'
        # }
        mysql_config_direct = {
            'user': 'oper_dc',
            'passwd': 'operzADF2020qwer',
            'host': '172.30.0.28',
            'port': 3306,
            # 'db': 'ph_data_bossjob'
        }
        # 连接数据库
        # self.mysql = pymysql.connect(**mysql_config)
        self.mysql = pymysql.connect(**mysql_config_direct)
        self.cursor = self.mysql.cursor()

    def fetch_one(self, sql):
        # 执行SQL
        self.cursor.execute(sql)
        # 查看结果
        result = self.cursor.fetchone()
        return result

    def fetch_all(self, sql):
        # 执行SQL
        self.cursor.execute(sql)
        # 查看结果
        result = self.cursor.fetchall()
        return result

    def update(self, sql):
        # 执行SQL
        self.cursor.execute(sql)
        self.mysql.commit()

    def close(self):
        self.cursor.close()  # 关闭查询
        self.mysql.close()
        # self.server.close()  # 关闭服务


if __name__ == '__main__':
    cc = None
    try:
        cc = MySqlSSH()
        qq = cc.fetch_all("select * from iuap_apdoc_basedoc.org_orgs where code='100018'")
        print(qq)
    except Exception as e:
        print(e)
        print("fail")
    finally:
        cc.close()