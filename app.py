from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


@app.route('/api/users', methods=["POST"])
def create_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    print(f"Nombre: {name}")
    print(f"Email:{email}")

    return jsonify({"success":True})


# undersocre methods and properties
if __name__ == '__main__':
    app.run()
