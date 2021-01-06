import pymysql
import pymysql.cursors
import json
from datetime import datetime


class MysqlDbPipeline:
    def __init__(self):
        db = 'forsale_api'
        host = 'localhost'
        port = 3306
        user = 'root'
        passwd = ''

        self.db_conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset='utf8')
        self.db_cur = self.db_conn.cursor()

    def process_item(self, item, spider):
        dateTimeObj = datetime.now()
        dateTimeString = dateTimeObj.strftime('%Y-%m-%d %H:%M:%S')

        unique_listing_identifier = item['id']
        del item['id']

        sql = "INSERT INTO scrapy_data (source, unique_listing_identifier, data, deleted_at, created_at, updated_at) " \
              "VALUES ('huislijn', '" + unique_listing_identifier + "', '" + json.dumps(item) + "', null, '" + dateTimeString + "'," \
              "'" + dateTimeString + "')"

        self.db_cur.execute(sql)
        self.db_conn.commit()

        print('Insert finished')

        return item