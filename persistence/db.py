import pymysql


def get_connection():
    return pymysql.connect(
        host='localhost',
        user="root",
        password='250597Pi',
        database="dogodb"
    )
