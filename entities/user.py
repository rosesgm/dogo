import pymysql
from enums.value_permission import ValuePermission
from entities.permission import Permission
from persistence.db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
from enums.profile import Profile
from flask_login import UserMixin


def parse_bool(value) -> bool:
    if value is None:
        return False
    if isinstance(value, (bytes, bytearray)):
        return value == b'\x01'
    return bool(value)


class User (UserMixin):
    def __init__(self, id: int, name: str, email: str,
                 password: str, profile: Profile,
                 permissions: list, is_active: bool, ):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.profile = profile
        self.permissions = permissions
        self.active = is_active

    @property
    def is_active(self):
        return self.active

    def is_admin(self):
        return self.profile == Profile.ADMIN

    def has_permission(self, permission: ValuePermission) -> bool:
        if self.profile == Profile.ADMIN:
            return True
        return any(p.value == permission for p in self.permissions)

    def check_email_exists(email) -> bool:
        connection = get_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        sql = "SELECT email FROM user WHERE email = %s"
        cursor.execute(sql, (email,))

        row = cursor.fetchone()

        cursor.close()
        connection.close()
        return row is not None

    def save(name: str, email: str, password: str):
        try:
            connection = get_connection()
            cursor = connection.cursor()

            hash_password = generate_password_hash(password)

            sql = "INSERT INTO user (name, email, password, profile, is_active) VALUES (%s, %s, %s,%s,%s)"
            cursor.execute(sql, (name,
                                 email,
                                 hash_password,
                                 Profile.CUSTOMER.value,
                                 1
                                 ))

            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as e:
            print(f"Error al guardar el usuario: {e}")
            return False

    def check_login(email, password):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT id, name, email, password, profile, is_active FROM user WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user and check_password_hash(user['password'], password):
                permissions = Permission.get_permission_by_user(user["id"])
                profile_enum = Profile(int(user["profile"]))
                is_active = parse_bool(user["is_active"])
                return User(user["id"], user["name"], user["email"],
                            user["password"], profile_enum, permissions, is_active)
            return None
        except Exception as e:
            print(f"Error al verificar el login: {e}")
            return None


        #LIKE: busca por nombre o email
    @staticmethod
    def search(query: str):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            # LIKE: busca por nombre o email
            sql = """
                SELECT id, name, email, profile, is_active
                FROM user
                WHERE name LIKE %s OR email LIKE %s
            """
            like = f"%{query}%"
            cursor.execute(sql, (like, like))
            rows = cursor.fetchall()

            cursor.close()
            connection.close()

            users = []
            for row in rows:
                profile = Profile(
                    int(row["profile"])) if row["profile"] is not None else Profile.CUSTOMER
                is_active = parse_bool(row["is_active"])
                permissions = Permission.get_permission_by_user(row["id"])
                users.append(User(row["id"], row["name"], row["email"],
                                  None, profile, permissions, is_active))
            return users
        except Exception as ex:
            print(f"Error searching users: {ex}")
            return []

    def get_by_id(id):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT id, name, email, password, profile, is_active FROM user WHERE id = %s"
            cursor.execute(sql, (id,))

            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user:
                profile = Profile(int(user["profile"]))
                permission = Permission.get_permission_by_user(user["id"])

                if user["is_active"] is not None:

                    is_active = user["is_active"] == b'\x01'

                return User(
                    user["id"],
                    user["name"],
                    user["email"],
                    user["password"],
                    profile,
                    permission,
                    is_active
                )
            return None
        except Exception as e:
            print(f"Error al obtener el usuario por ID: {e}")
            return None

    def get_all():
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT id, name, email, profile, is_active FROM user"
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            connection.close()

            users = []
            for row in rows:
                profile = Profile(
                    int(row["profile"])) if row["profile"] is not None else Profile.CUSTOMER
                is_active = parse_bool(row["is_active"])
                permissions = Permission.get_permission_by_user(row["id"])
                users.append(User(row["id"], row["name"], row["email"],
                                  None, profile, permissions, is_active))
            return users
        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
            return []

    def toggle_active(user_id: int, new_status: bool):
        try:
            connection = get_connection()
            cursor = connection.cursor()

            sql = "UPDATE user SET is_active = %s WHERE id = %s"
            cursor.execute(sql, (new_status, user_id))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as e:
            print(f"Error al actualizar estado del usuario: {e}")
            return False

    def get_account_by_id(id):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT id, number FROM account WHERE id = %s"
            cursor.execute(sql, (id,))

            account = cursor.fetchone()

            cursor.close()
            connection.close()

            if account:
                return account.Account(
                    account["id"],
                    account["number"],
                    account["user_id"]
                )
            return None
        except Exception as e:
            print(f"Error al obtener el usuario por ID: {e}")
            return None
