from datetime import datetime
from enums.transaction_type import TransactionType
from persistence.db import get_connection
import pymysql

class Transaction():
    def __init__(self, id: int, description: str, date: datetime, amount: float, type: TransactionType):
        self.id = id
        self.description = description
        self.date = date
        self.amount = amount
        self.type = type

    @staticmethod
    def get_transaction_by_account(id_account: int):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT id, description, date, amount, type FROM transaction WHERE id_account = %s"
            cursor.execute(sql, (id_account,))

            rs = cursor.fetchall()
            transactions = []

            for row in rs:
                transactions.append(Transaction(
                    row["id"],
                    row["description"],
                    row["date"],
                    row["amount"],
                    TransactionType(row["type"])
                ))

            cursor.close()
            connection.close()
            return transactions

        except Exception as ex:
            print(f"Error getting transaction by account: {ex}")
            return []