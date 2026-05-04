from persistence.db import get_connection
from entities.user import User
from datetime import datetime
from enums.log_type import LogType
import pymysql


class Log:

    def __init__(self, id: int, date: datetime, user_name: str,
                 description: str, log_type: LogType):
        self.id = id
        self.date = date
        self.user_name = user_name
        self.description = description
        self.log_type = log_type

    @staticmethod
    def save(user, description: str, type: LogType):
        try:
            connection = get_connection()
            cursor = connection.cursor()

            sql = """
                INSERT INTO log (id_user, description, type, date)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (user.id, description,
                           type.value, datetime.now()))

            connection.commit()
            cursor.close()
            connection.close()

            return True

        except Exception as ex:
            print(f"Error saving log: {ex}")
            return False

    @staticmethod
    def get_all():
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = """
                SELECT 
                    l.id, 
                    l.date, 
                    l.description, 
                    l.type, 
                    u.name AS user_name
                FROM log l
                INNER JOIN user u ON l.id_user = u.id
                ORDER BY l.date DESC
            """

            cursor.execute(sql)
            rows = cursor.fetchall()

            logs = []

            for row in rows:
                logs.append(Log(
                    id=row["id"],
                    date=row["date"],
                    user_name=row["user_name"],
                    description=row["description"],
                    log_type=LogType(row["type"])
                ))

            cursor.close()
            connection.close()

            return logs

        except Exception as ex:
            print(f"Error al obtener logs: {ex}")
            return []
