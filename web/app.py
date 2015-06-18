#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from wtforms import TextField, HiddenField, SubmitField, PasswordField
from flask_wtf import Form
from wtforms.validators import Required, Email
from redis import Redis

from justDespair import JustEat, LoginException

import os

REGION="ie"
CURRENCY=u"€"
TOTAL_PATH="/var/tmp/justdespair_total.txt"
# CHANGEME obviously.
SECRET_KEY="ir8joo3ieN1ahbaeNg1oor1Chawoo4"

REDIS_KEY = "justdespair_total"

class LoginForm(Form):
    username = TextField('Username', description='The JustEat username.',
                         validators=[Required("Username is required!"),
                                     Email("JustEat usernames need to be email addresses!")])
    password = PasswordField('Password', description='The JustEat password.',
                         validators=[Required("Password is required!")])
    submit_button = SubmitField('Submit Form')

def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    # Yes, this is overkill but this system is running a redis server
    # already. Fuckin deal with it.
    redis = Redis()

    app.config['SECRET_KEY'] = SECRET_KEY

    current_high_total = 0

    # if os.path.exists(TOTAL_PATH):
    #     with open(TOTAL_PATH) as total_f:
    #         current_total_data = total_f.read().strip()
    #         check_total = current_total_data.strip("0123456789.")
    #         if check_total:
    #             raise Exception("Current total data is in an unexpected format. Exiting")
    #         else:
    #             current_high_total = current_total_data

    if redis.exists(REDIS_KEY):
        current_high_total = float(redis.get(REDIS_KEY))

    @app.route("/faq", methods=("GET",))
    def faq():
        return render_template("faq.html")

    @app.route("/", methods=("GET", "POST"))
    def render_page():
        if request.method == 'POST':
            try:
                just_eat = JustEat(request.form["username"],
                                   request.form["password"],
                                   REGION)
                order_data = just_eat.getOrderData()
            except Exception as e:
                return render_template("error.html")

            total_data = []
            for year, year_details in order_data.iteritems():
                total_data.append(year_details["total_cost"])
            total_cost = sum(total_data)

            new_record = False
            if total_cost > current_high_total:
                new_record = True
                redis.set(REDIS_KEY, total_cost)
            elif total_cost == current_high_total:
                new_record = True

            return render_template(
                "results.html",
                new_record=new_record,
                total_cost=total_cost,
                record_cost=current_high_total,
                currency=CURRENCY,
                order_data=order_data
            )
        else:
            form = LoginForm()
            return render_template("login.html", form=form)

    return app

if __name__ == '__main__':
    create_app().run(debug=False)
