from datetime import datetime
from entities.user import User
from entities.transaction import Transaction
from persistence.db import get_connection
import pymysql


class Account():

    def __init__(self, id: int, number: str, creation_date: datetime, user: User, transaction: list):
        self.id = id
        self.number = number
        self.creation_date = creation_date
        self.user = user
        self.transaction = transaction
    @staticmethod
    def get_account_by_user(id_user: int):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT id, number, creation_date, id_user FROM account WHERE id_user= %s"
            cursor.execute(sql, (id_user,))

            rs = cursor.fetchone()
            if rs is None:
                cursor.close()
                connection.close()
                return None

            user = User.get_by_id(rs["id_user"])
            transactions = Transaction.get_transaction_by_account(rs["id"])
            account = Account(
                rs["id"],
                rs["number"],
                rs["creation_date"],
                user,
                transactions

            )
            cursor.close()
            connection.close()
            return account
        except Exception as ex:
            print(f"Error getting account by user:{ex}")
            return False
