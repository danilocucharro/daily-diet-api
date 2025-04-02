import bcrypt
from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from database import db
from models.meal import Meal
from models.user import User

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:admin1234@127.0.0.1:3306/daily-diet-api"

login_manager = LoginManager()

db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


"""AUTHENTICATION ROUTES"""
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()
        if user.username == username and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            print(user)
            login_user(user)
            return jsonify({"message": "Autenticacao realizada com sucesso"})

    return jsonify({"message": "Credenciais inválidas"}), 404

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "logout realizado com sucesso"})


"""USER ROUTES"""
@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        is_user_exists = User.query.filter_by(username=username).first()
        if is_user_exists.username == username:
            return jsonify({"message": "esse nome usuário já existe"}), 409

        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "usuário cadastrado com sucesso"})

    return jsonify({"message": "não foi possivel fazer o cadastro"}), 400


"""MEAL ROUTES"""
@app.route("/meal", methods=["POST"])
@login_required
def create_meal():
    data = request.json
    name = data.get("name")
    description = data.get("description")
    is_on_diet = data.get("is_on_diet")
    date_and_hour = data.get("date_and_hour")

    if name and description and is_on_diet and date_and_hour:
        new_meal = Meal(
            name=name,
            description=description,
            is_on_diet= is_on_diet,
            date_and_hour=date_and_hour,
            user_id=current_user.id
        )
        db.session.add(new_meal)
        db.session.commit()
        return jsonify({"message": "refeição cadastrada com sucesso!"})

    return jsonify({"message": "Dados invalidos"}), 400


@app.route("/meal/<int:meal_id>", methods=["PUT"])
@login_required
def update_meal(meal_id):
    data = request.json
    meal = Meal.query.get(meal_id)
    new_name = data.get("name")
    new_description = data.get("description")
    new_is_on_diet = data.get("is_on_diet")
    new_date_and_hour = data.get("date_and_hour")
    if meal:
        if new_name and new_description and new_is_on_diet and new_date_and_hour:
            if meal.user_id == current_user.id: # apenas o usuario que criou a refeicao podera edita-la
                meal.name = new_name
                meal.description = new_description
                meal.is_on_diet = new_is_on_diet
                meal.date_and_hour = new_date_and_hour
                db.session.commit()

                return jsonify({"message": "refeição atualizada com sucesso"})
            return jsonify({"message": "Ação não permitida"}), 403

        return jsonify({"message": "dados invalidos"}), 400
    return jsonify({"message": f"refeição {meal_id} não foi encontrada"}), 404


@app.route("/meal/<int:meal_id>", methods=["DELETE"])
@login_required
def delete_meal(meal_id):
    meal = Meal.query.get(meal_id)

    if meal:
        if meal.user_id != current_user.id:
            return jsonify({"message": "Ação não permitida"}), 403
        else:
            db.session.delete(meal)
            db.session.commit()
            return jsonify({"message": f"refeição {meal_id} deletada com sucesso"})

    return jsonify({"message": "refeição não foi encontrada"}), 404

if __name__ == "__main__":
    app.run(debug=True)