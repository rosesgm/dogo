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


        """VIEW, Consulta la vista v_account_summary definida en la base de datos
        la vista ejecuta INNEr JOIN entre user y account
        LEFT JOIN con transaction Y GROUP Y para agrupar transacciones por cuenta"""
    @staticmethod
    def get_summary():
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM v_account_summary")
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            result = []
            for row in rows:
                result.append({
                    "user_id": row["user_id"],
                    "user_name": row["user_name"],
                    "email": row["email"],
                    "account_id": row["account_id"],
                    "account_number": row["account_number"],
                    "balance": float(row["balance"]),
                    "creation_date": str(row["creation_date"]),
                    "total_transactions": row["total_transactions"]
                })
            return result
        except Exception as ex:
            print(f"Error getting account summary: {ex}")
            return []


        """"JOIN + GROUP BY + HAVING"""
    @staticmethod
    def get_top_users(min_transactions: int):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = """
                SELECT
                    u.name              AS user_name,
                    a.number            AS account_number,
                    a.balance,
                    COUNT(t.id)         AS total_transactions,
                    SUM(t.amount)       AS total_volume
                FROM user u
                INNER JOIN account     a ON a.id_user    = u.id
                INNER JOIN transaction t ON t.id_account = a.id
                GROUP BY u.id, u.name, a.number, a.balance
                HAVING COUNT(t.id) >= %s
                ORDER BY total_transactions DESC
            """
            cursor.execute(sql, (min_transactions,))
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            result = []
            for row in rows:
                result.append({
                    "user_name": row["user_name"],
                    "account_number": row["account_number"],
                    "balance": float(row["balance"]),
                    "total_transactions": row["total_transactions"],
                    "total_volume": float(row["total_volume"] or 0)
                })
            return result
        except Exception as ex:
            print(f"Error getting top users: {ex}")
            return []


        """"INNER JOIN + Subquery para obtener cuentas sin transacciones"""
    @staticmethod
    def get_inactive_accounts():
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = """
                SELECT
                    a.id            AS account_id,
                    a.number        AS account_number,
                    a.creation_date,
                    u.name          AS user_name,
                    u.email
                FROM account a
                INNER JOIN user u ON u.id = a.id_user
                WHERE a.id NOT IN (
                    SELECT DISTINCT id_account FROM transaction
                )
                ORDER BY a.creation_date DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            result = []
            for row in rows:
                result.append({
                    "account_id": row["account_id"],
                    "account_number": row["account_number"],
                    "creation_date": str(row["creation_date"]),
                    "user_name": row["user_name"],
                    "email": row["email"]
                })
            return result
        except Exception as ex:
            print(f"Error getting inactive accounts: {ex}")
            return []


    @staticmethod
    def get_top_users(min_transactions: int):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            # JOIN + GROUP BY + HAVING
            sql = """
                SELECT
                    u.name          AS user_name,
                    a.number        AS account_number,
                    a.balance,
                    COUNT(t.id)     AS total_transactions,
                    SUM(t.amount)   AS total_volume
                FROM user u
                INNER JOIN account a ON a.id_user = u.id
                INNER JOIN transaction t ON t.id_account = a.id
                GROUP BY u.id, u.name, a.number, a.balance
                HAVING COUNT(t.id) >= %s
                ORDER BY total_transactions DESC
            """
            cursor.execute(sql, (min_transactions,))
            rows = cursor.fetchall()

            cursor.close()
            connection.close()
            return rows
        except Exception as ex:
            print(f"Error getting top users: {ex}")
            return []


    @staticmethod
    def get_inactive_accounts():
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            # Subquery: cuentas sin ninguna transacción
            sql = """
                SELECT a.id, a.number, a.creation_date, u.name AS user_name
                FROM account a
                INNER JOIN user u ON u.id = a.id_user
                WHERE a.id NOT IN (
                    SELECT DISTINCT id_account FROM transaction
                )
            """
            cursor.execute(sql)
            rows = cursor.fetchall()

            cursor.close()
            connection.close()
            return rows
        except Exception as ex:
            print(f"Error getting inactive accounts: {ex}")
            return []
