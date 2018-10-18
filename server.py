from flask import Flask, render_template, redirect, session, request, flash
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'boopboop'
mysql = connectToMySQL('login-reg')
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    mysql = connectToMySQL('login-reg')
    query = "SELECT * FROM users WHERE Email = %(Email)s;"
    data = {'Email': request.form['email']}
    checkEmail = mysql.query_db(query,data)

    errors = 0
    if len(request.form['first_name']) < 2:
        flash("First name must be at least 2 characters long.")
        errors += 1
    if len(request.form['last_name']) < 2:
        flash("Last name must be at least 2 characters long.")
        errors += 1
    if len(request.form['email']) < 1:
        flash("Email address cannot be blank.")
        errors += 1
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid email address.")
        errors += 1
    if checkEmail:
        flash("Email address already registered.")
        errors += 1
    if len(request.form['password']) < 1:
        flash("Password cannot be blank.")
        errors += 1
    if request.form['password'] != request.form['confirm_password']:
        flash("Passwords do not match.")
        errors += 1

    if errors:
        return render_template('index.html')
    else:
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        mysql = connectToMySQL("login-reg")
        query = "INSERT INTO users (FirstName, LastName, Email, Password, CreatedAt, UpdatedAt) VALUES (%(FirstName)s, %(LastName)s, %(Email)s, %(Password)s, NOW(), NOW());"
        data = {
             'FirstName': request.form['first_name'],
             'LastName':  request.form['last_name'],
             'Email': request.form['email'],
             'Password': pw_hash}
        new_user = mysql.query_db(query, data)
        return redirect('/success')

@app.route('/login', methods=['POST'])
def login():
    mysql = connectToMySQL("login-reg")
    query = "SELECT * FROM users WHERE Email = %(Email)s;"
    data = { 'Email' : request.form["login_email"] }
    result = mysql.query_db(query, data)
    if result:
        if bcrypt.check_password_hash(result[0]['Password'], request.form['login_password']):
            return redirect('/success')

    flash("Email and/or password is incorrect.")
    return render_template('index.html')

@app.route('/success')
def success():
    return render_template('success.html')

if __name__=="__main__":
    app.run(debug=True)