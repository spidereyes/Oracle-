from DBUtils.PooledDB import PooledDB
import cx_Oracle
import os
host = "127.0.0.1"
username = "c##zq"
password = "zouqing1999"
port = 1521
database = ""
encoding = "utf-8"
pool = PooledDB(creator=cx_Oracle,
                user=username,
                password=password,
                dsn="{host}:{port}/ORCL".format(host=host, port=port),
                )
class Config:
    DEBUG = True
    SECRET_KEY = "secret key"
    DOWNLOADPATHS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads\\student')
    DOWNLOADPATHA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads\\admin')
    DOWNLOADPATHT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads\\teacher')
    DOWNLOADPATHP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads\\post')
    DEFAULTPIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
    DATABASE=pool
