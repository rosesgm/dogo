from flask import Flask, render_template, request, jsonify, redirect, url_for
from entities.user import User
from entities.account import Account
from entities.permission import Permission
from entities.log import Log
from entities.transaction import Transaction
from enums.log_type import LogType
from enums.transaction_type import TransactionType
from enums.value_permission import ValuePermission
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route('/welcome')
@login_required
def welcome():
    account = Account.get_account_by_user(current_user.id)
    logs = Log.get_all() if current_user.is_admin() else []
    return render_template('welcome.html', account=account,
                           ValuePermission=ValuePermission, logs=logs)


@app.route('/api/users', methods=["POST"])
def create_user():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if User.check_email_exists(email):
        return jsonify({"success": False, "message": "El correo electrónico ingresado ya se encuentra registrado."}), 409

    if User.save(name, email, password):
        return jsonify({"success": True, "message": "Su cuenta fue creada correctamente."}), 201
    else:
        return jsonify({"success": False, "message": "Ocurrió un error al crear su cuenta. Intente de nuevo"}), 500


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.check_login(email, password)

    if user:
        if not user.is_active:

            return jsonify({
                "success": False,
                "message": "Su cuenta ha sido desactivada. Comuníquese con el administrador del sistema."
            }), 403
        login_user(user)

        # Invocar metodo
        Log.save(user, "Inicio de sesión exitoso", LogType.LOGIN)
        return jsonify({
            "success": True,
            "message": "Sesión iniciada correctamente"
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Los datos de acceso ingresados no son correctos."
        }), 401


@app.route("/api/users", methods=["GET"])
@login_required
def get_users():
    if current_user.profile.name != "ADMIN":
        return jsonify({
            "success": False,
            "message": "Acceso no autorizado"
        }), 403

    users = User.get_all()

    return jsonify({
        "success": True,
        "users": users
    })


@app.route("/users")
@login_required
def users():
    if not current_user.is_admin():
        return "Acceso no autorizado", 403
    all_users = User.get_all()
    all_permissions = ValuePermission
    return render_template("users.html", users=all_users,
                           ValuePermission=all_permissions)


@app.route("/api/users/<int:user_id>/toggle", methods=["POST"])
@login_required
def toggle_user(user_id):
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

    data = request.get_json()
    new_status = data.get("is_active")

    if User.toggle_active(user_id, new_status):
        estado = "activado" if new_status else "desactivado"
        return jsonify({"success": True, "message": f"Usuario {estado} correctamente."})
    return jsonify({"success": False, "message": "Error al actualizar el usuario."}), 500


@app.route("/api/users/<int:user_id>/permissions", methods=["POST"])
@login_required
def add_permission(user_id):
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

    data = request.get_json()
    value = data.get("value")

    try:
        permission_enum = ValuePermission(int(value))
    except (ValueError, KeyError):
        return jsonify({"success": False, "message": "Permiso no válido."}), 400

    success, message = Permission.add_permission(user_id, permission_enum)
    status = 200 if success else 409
    return jsonify({"success": success, "message": message}), status


@app.route("/api/users/<int:user_id>/permissions/<int:value>", methods=["DELETE"])
@login_required
def delete_permission(user_id, value):
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

    try:
        permission_enum = ValuePermission(value)
    except (ValueError, KeyError):
        return jsonify({"success": False, "message": "Permiso no válido."}), 400

    success, message = Permission.delete_permission(user_id, permission_enum)
    return jsonify({"success": success, "message": message})


@app.route("/logs")
@login_required
def logs():
    if not current_user.is_admin():
        return "Acceso no autorizado", 403

    logs = Log.get_all()

    print("TOTAL LOGS:", len(logs))
    print("LOGS:", logs)

    return render_template("logs.html", logs=logs)


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

#NUEVOS ENDPOINTS

@app.route("/api/transactions", methods=["POST"])
@login_required
def create_transaction():
    if not current_user.has_permission(ValuePermission.TRANSACTION_COMMIT):
        return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

    data = request.get_json()
    id_account = data.get("id_account")
    description = data.get("description")
    amount = float(data.get("amount", 0))
    type_value = data.get("type")  # 1=INCOME, 2=EXPENSE

    try:
        transaction_type = TransactionType(int(type_value))
    except (ValueError, KeyError):
        return jsonify({"success": False, "message": "Tipo de transacción no válido."}), 400

    success, message = Transaction.save(
        id_account, description, amount, transaction_type)
    if success:
        Log.save(
            current_user, f"Transacción {transaction_type.name} por ${amount}", LogType.SAVE)

    status = 201 if success else 400
    return jsonify({"success": success, "message": message}), status


@app.route("/api/accounts/summary", methods=["GET"])
@login_required
def accounts_summary():
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

    rows = Account.get_summary()
    return jsonify({"success": True, "data": rows})


@app.route("/api/accounts/top-users", methods=["GET"])
@login_required
def top_users():
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

    min_t = request.args.get("min_transactions", 1)
    rows = Account.get_top_users(int(min_t))
    return jsonify({"success": True, "data": rows})


@app.route("/api/accounts/inactive", methods=["GET"])
@login_required
def inactive_accounts():
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

    rows = Account.get_inactive_accounts()
    return jsonify({"success": True, "data": rows})


@app.route("/api/users/search", methods=["GET"])
@login_required
def search_users():
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Acceso no autorizado"}), 403

    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"success": False, "message": "Parámetro de búsqueda requerido."}), 400

    users = User.search(q)
    return jsonify({
        "success": True,
        "users": [{"id": u.id, "name": u.name, "email": u.email} for u in users]
    })


if __name__ == '__main__':
    app.run()
