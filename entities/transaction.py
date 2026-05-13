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

        """"START TRANSACTION / COMMIT / ROLLBACK + TRIGGER 
        para actualizar balance de cuenta automáticamente al insertar transacción."""
    @staticmethod
    def save(id_account: int, description: str, amount: float, type: TransactionType):
        connection = get_connection()
        try:
            connection.begin()
            cursor = connection.cursor()

            # Verificar que la cuenta existe
            cursor.execute(
                "SELECT id, balance FROM account WHERE id = %s", (id_account,))
            account = cursor.fetchone()
            if not account:
                connection.rollback()
                return False, "La cuenta no existe."

            # Si es retiro, verificar saldo suficiente
            if type == TransactionType.EXPENSE and account[1] < amount:
                connection.rollback()
                return False, "Saldo insuficiente."

            # Insertar transacción — el TRIGGER actualiza el balance automáticamente
            sql = """
                INSERT INTO transaction (description, date, amount, type, id_account)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (description, datetime.now(),
                           amount, type.value, id_account))

            connection.commit()
            cursor.close()
            connection.close()
            return True, "Transacción realizada correctamente."

        except Exception as ex:
            connection.rollback()
            print(f"Error saving transaction: {ex}")
            return False, "Error al realizar la transacción."
