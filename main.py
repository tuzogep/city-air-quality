import requests
from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from datetime import datetime
import os

TOKEN = os.environ.get("TOKEN")
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)


def get_aqi(city="Vienna"):
    response = requests.get(f"http://api.waqi.info/feed/{city}/?token={TOKEN}")
    response.raise_for_status()
    data = response.json()
    print(data)
    answer = {
        "city": data["data"]["city"]["name"],
        "aqi": data["data"]["aqi"],
        "geo0": data["data"]["city"]["geo"][0],
        "geo1": data["data"]["city"]["geo"][1],
        "widget_city": data["data"]["city"]["url"].replace("https://aqicn.org/city/", "")
    }
    return answer


class CityForm(FlaskForm):
    city = StringField("Search for a city by name:", validators=[DataRequired()], render_kw={"placeholder": "City name..."})
    submit = SubmitField("Search")


@app.route('/', methods=["GET", "POST"])
def home():
    aqi_data = get_aqi()
    form = CityForm()
    if form.validate_on_submit():
        user_input_city = form.city.data
        try:
            aqi_data = get_aqi(user_input_city)
        except TypeError:
            message = f"Cannot find the city: {user_input_city}."
            flash(message)
            aqi_data = get_aqi()
        return render_template("index.html", aqi=aqi_data, form=form)
    return render_template("index.html", aqi=aqi_data, form=form, now=datetime.utcnow())


if __name__ == "__main__":
    app.run(debug=True, port=5002)
