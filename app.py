#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  1 10:54:46 2023

@author: brendan
"""

from flask import Flask, request, session, redirect, flash, url_for, jsonify
from flask.templating import render_template
import sqlite3
import json
import logging


app = Flask(__name__)
app.debug = True
app.secret_key = 'admin'
app.logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
app.logger.addHandler(console_handler)

@app.route('/scores')
def load_global_scores():
    conn = sqlite3.connect('TopRankTanks.db')
    c = conn.cursor()
    c.execute('SELECT * FROM scores ORDER BY score DESC LIMIT 5')
    scores = [{'username': row[1], 'score': row[2]} for row in c.fetchall()]
    return scores
    

def load_local_scores():
    conn = sqlite3.connect('TopRankTanks.db')
    c = conn.cursor()
    c.execute('SELECT * FROM scores ORDER BY score DESC LIMIT 5')
    rows = c.fetchall()
    scores = []
    for row in rows:
        scores.append({'score': row[0]})
    conn.close()
    return json.dumps({'data': scores})


@app.route('/login', methods=['POST', 'GET'])
def login():
    conn = sqlite3.connect('TopRankTanks.db')
    cur = conn.cursor()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
    
        if user is None:
            session['error'] = 'Invalid username'
            return render_template('login.html', error=session.get('error'))
    
        if user[1] != password:
            session['error'] = 'Incorrect password'
            return render_template('login.html', error=session.get('error'))
    
        session['username'] = username
        return redirect(url_for('main_menu', username=username))
    else:
        session.pop('error', None)
        return render_template('login.html', error=None)

@app.route('/main_menu/<string:username>')
def main_menu(username):
    username = request.args.get('username')
    scores = load_global_scores()
    return render_template('MainMenu.html',username=username,scores=scores)

@app.route('/account', methods=['POST','GET'])
def account():
    
    conn = sqlite3.connect('TopRankTanks.db')
    cur = conn.cursor()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        
        if user is None:
            if(password != confirm):
                session['error'] = 'Passwords do not match'
                return render_template('account.html', error=session.get('error'))
            else:
                cur.execute("INSERT INTO users (username, password) VALUES (?,?)", (username,password))
                conn.commit()
                return redirect('/login')
                
        else:
            session['error'] = 'Username already exists'
            return render_template('account.html', error=session.get('error'))
        
    return render_template('Account.html')

    
@app.route('/')
def index():
    return render_template('Login.html')

if __name__ == '__main__':
    app.run()