from cProfile import label
from dataclasses import dataclass
from distutils.command.upload import upload
from fileinput import filename
from msilib.schema import File
from tkinter import Canvas
from tkinter.messagebox import NO
from unittest import result
from click import style

from sqlalchemy import null
from market import app
from flask import render_template, redirect, request, url_for, flash, Response
from market.models import Item, User, Upload
from market.forms import RegisterForm, LoginForm
from market import db
from flask_login import current_user, login_user, logout_user, login_required
import pandas as pd
import pickle
import sklearn
from io import BytesIO
import random
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure



@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market')
@login_required
def market_page():
    items = Item.query.all()
    return render_template('market.html', items=items)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('predict_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('predict_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict_page():

    file = None
    values = None
    labels = None
    if request.method == 'POST':
        file = request.files['file']

        upload = Upload(filename=file.filename, data=file.read(), owner=current_user.id)
        file = upload
        db.session.add(upload)
        db.session.commit()

    if request.method == 'GET':
        if current_user.files:
            file = Upload.query.filter_by(filename=(current_user.files)[-1].filename).first()

    if file:
        loaded_model = pickle.load(open('ref_model', 'rb'))
        dftrain = pd.read_csv(BytesIO(file.data), usecols=[1, 2])
        values = loaded_model.predict(dftrain)
        
        labels = [i for i in range(len(values))]
        values = [i for i in values]

    return render_template('predict.html', file=file, values=values, labels=labels)
