from flask import Flask, request, jsonify
from database import db
from models.meal import Meal

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:admin1234@127.0.0.1:3306/daily-diet-api"

db.init_app(app)

@app.route("/meal", methods=["POST"])
def create_meal():
    data = request.json
    name = data.get("name")
    description = data.get("description")
    is_on_diet = data.get("is_on_diet")
    date_and_hour = data.get("date_and_hour")

    if name and description and is_on_diet and date_and_hour:
        new_meal = Meal(name=name, description=description, is_on_diet= is_on_diet, date_and_hour=date_and_hour)
        db.session.add(new_meal)
        db.session.commit()
        return jsonify({"message": "refeição cadastrada com sucesso!"})

    return jsonify({"message": "Dados invalidos"}), 404

if __name__ == "__main__":
    app.run(debug=True)