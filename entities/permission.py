import pymysql
from enums.value_permission import ValuePermission
from persistence.db import get_connection


class Permission:
    def __init__(self, id: int, value: ValuePermission):
        self.id = id
        self.value = value

    def get_permission_by_user(id_user):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT id, value FROM permission WHERE id_user = %s"
            cursor.execute(sql, (id_user,))

            rs = cursor.fetchall()

            permissions = []

            for row in rs:
                permissions.append(
                    Permission(row["id"], ValuePermission(row["value"])))
            cursor.close()
            connection.close()

            return permissions

        except Exception as e:
            print(f"Error al obtener permisos del usuario: {e}")
            return []
    def has_permission(id_user, value_permission):
        permissions = Permission.get_permission_by_user(id_user)
        for p in permissions:
            if p.value == value_permission:
                return True
        return False

    def add_permission(id_user: int, value: ValuePermission):
        try:
            if Permission.has_permission(id_user, value):
                return False, "El usuario ya tiene este permiso."
 
            connection = get_connection()
            cursor = connection.cursor()
 
            sql = "INSERT INTO permission (id_user, value) VALUES (%s, %s)"
            cursor.execute(sql, (id_user, value.value))
            connection.commit()
            cursor.close()
            connection.close()
            return True, "Permiso agregado correctamente."
 
        except Exception as e:
            print(f"Error al agregar permiso: {e}")
            return False, "Error al agregar el permiso."
 
    def delete_permission(id_user: int, value: ValuePermission):
        try:
            connection = get_connection()
            cursor = connection.cursor()
 
            sql = "DELETE FROM permission WHERE id_user = %s AND value = %s"
            cursor.execute(sql, (id_user, value.value))
            connection.commit()
            cursor.close()
            connection.close()
            return True, "Permiso eliminado correctamente."
 
        except Exception as e:
            print(f"Error al eliminar permiso: {e}")
            return False, "Error al eliminar el permiso."
