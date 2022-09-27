
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
class GetMongo:
    def _connect_mongo(self, host, port, username, password, db):
        if username and password:
            mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
            conn = MongoClient(mongo_uri)
        else:
            conn = MongoClient(host, port)
        return conn
    def read_mongo(self,db, collection, query={}, host='localhost', port=27017, username=None, password=None, no_id=True,get_pd=True):
        get_client = self._connect_mongo(host=host, port=port, username=username, password=password, db=db)
        cursor = get_client[db][collection].find(query)
        # 쿼리의 결과가 없다면 None return
        if not list(cursor.clone()):
            get_client.close()
            return None
        if get_pd:
            df =  pd.DataFrame(list(cursor))
            if no_id:
                del df['_id']
            get_client.close()
            return df
        else:
            result = list(cursor.clone())
            get_client.close()
            return result
    def read_collection_list(self,db,host='localhost',port=27017,username=None,password=None):
        get_client = self._connect_mongo(host=host,port=port,username=username,password=password,db=db)
        c_list = get_client[db].list_collection_names()
        get_client.close()
        return c_list
class GetData(GetMongo):
    def __init__(self,m_id,spec,no_id=True):
        self.m_id = m_id
        self.spec = spec
        self.current_data = self.init_data_from_mongo(m_id,spec,no_id)
    def init_data_from_mongo(self,m_id,spec,no_id):
        query = {"m_id" : m_id}
        return self.read_mongo("test-db",collection=spec,query=query,no_id=no_id)
    def get_data_from_mongo(self,m_id,spec):
        if self.m_id != m_id or self.spec != spec:
            return GetData(m_id,spec)
        else:
            return self
    def get_data_from_mongo_by_date(self,s_datetime,e_datetime):
        s_datetime = datetime.strptime(s_datetime, '%Y-%m-%d %H:%M:%S')
        e_datetime = datetime.strptime(e_datetime, '%Y-%m-%d %H:%M:%S')
        temp_pd = self.current_data
        temp_pd['datetime'] = pd.to_datetime(self.current_data['datetime'])
        return temp_pd[(temp_pd['datetime']>=s_datetime) & (temp_pd['datetime']<e_datetime)]


