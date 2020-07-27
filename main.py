# Todd McCullough  June 29 2020

from datetime import date, datetime, timedelta
from flask import Flask
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import co_main

import db
import functools
import numpy as np
import os
import pandas as pd
import re


theme = 'beige'
month, day, weekday = co_main.get_weekday()
yesterday = str(int(day)-1)

on_db = pd.read_csv('datasets/2020/conposcovidloc.csv')
on_age = pd.read_csv('datasets/2020/age_groups_ontario.csv')

total_cases = on_db['Accurate_Episode_Date'].count()

co = Flask(__name__, instance_relative_config=True)
co.config.from_mapping(
        SECRET_KEY='dev', # change to a random value later when deploying
        DATABASE=os.path.join(co.instance_path, 'main.sqlite'),
    )

def get_value(connect,userid,string):
    table = string+'_t'
    select = f'SELECT {string} FROM {table} WHERE author_id = ? ORDER BY id DESC LIMIT 1'
    value = connect.execute(select, (userid,)).fetchone()
    return value[0]

def insert_query(connect,userid,query,column):
    if not query:
        pass
    else:
        table = column+'_t'
        query = "INSERT INTO "+table+f" (author_id, {column}) VALUES ({userid}, '{query}')"
        connect.execute(query)
        connect.commit()

@co.route('/index')
def index():

    today = date.today().strftime('%Y-%m-%d')
    check = open('previous.txt','r')
    check = re.sub('\n','',check.read())

    utc_today = co_main.utc_convert(today)

    if today != check:
        
        # get the current file if it hasn't been updated today
        co_main.update_files(utc_today)

        return render_template('co-update.html',
        day = day, weekday = weekday, month = month,
        theme = theme)

    connect = db.get_db()
    error = None

    gender_groups = pd.read_csv('datasets/2020/gender_infected.csv')
    infected = pd.read_csv('datasets/2020/infected.csv')
    outcomes = pd.read_csv('datasets/2020/outcomes.csv')
    resolved = round(outcomes.at[0,'pop%']*100,2)
    fatal = round(outcomes.at[1,'pop%']*100,2)
    active = round(outcomes.at[2,'pop%']*100,2)

    return render_template('co-index.html',
    day = day, weekday = weekday, month = month, yesterday = yesterday,
    infected = infected, gender_groups = gender_groups,
    resolved = resolved, fatal = fatal, active = active, total_cases = total_cases,
    theme = theme)

@co.route('/update')
def update():

    connect = db.get_db()
    error = None

    return render_template('co-update.html',
    day = day, weekday = weekday, month = month,
    theme = theme)

db.init_app(co)

if __name__ == "__main__":
    co.run()