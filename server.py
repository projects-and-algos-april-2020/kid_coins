from flask import Flask, render_template, request, session, flash, redirect
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
app.secret_key = "keep it secret"

bcrypt = Bcrypt(app)
schema = "kid_coins"

@app.route('/')
def log_reg_landing():
    return render_template("login_reg.html")

@app.route('/on_register', methods=['POST'])
def on_register():
    is_valid = True

    if len(request.form['em']) < 1:
        is_valid = False
        flash("Please enter an email")
    elif not EMAIL_REGEX.match(request.form['em']):
        is_valid = False
        flash("Please enter a valid email")
    else:
        mysql = connectToMySQL(schema)
        query = 'SELECT * FROM users WHERE email = %(em)s;'
        data = {
            'em':request.form['em']
        }
        user = mysql.query_db(query,data)
        if user:
            is_valid = False
            flash("email already in use")

    if len(request.form['fn']) < 2:
        is_valid=False
        flash("Fist name must be atleast 2 characters long.")
    if len(request.form['ln']) < 2:
        is_valid=False
        flash("last name must be atleast 2 characters long.")
    if len(request.form['pw']) < 8:
        is_valid=False
        flash("password must be atleast 8 characters long.")

    if request.form['pw'] != request.form['cpw']:
        is_valid=False
        flash("Passwords must match")

    if is_valid:
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES ( %(fn)s, %(ln)s, %(em)s, %(pw)s, NOW(), NOW())"
        data = {
            "fn": request.form['fn'],
            "ln": request.form['ln'],
            "em": request.form['em'],
            "pw": bcrypt.generate_password_hash(request.form['pw'])
        }
        mysql = connectToMySQL(schema)
        user_id = mysql.query_db(query,data)

        if user_id:
            session['user_id'] = user_id
            session['name'] = request.form['fn']
            return redirect ('/home')

    return redirect('/')

@app.route("/on_login", methods=["POST"])
def on_login():
    is_valid = True

    if not EMAIL_REGEX.match(request.form['em']):
        is_valid = False
        flash("email is not valid")

    if is_valid:
        query = "SELECT users.id, users.first_name, users.password FROM users WHERE users.email = %(em)s"
        data = {
            'em': request.form['em']
        } 
        mysql = connectToMySQL(schema)
        result = mysql.query_db(query, data)

        if result:
            if not bcrypt.check_password_hash(result[0]['password'], request.form['pw']):
                flash("incorrect password and/or email")
                return redirect('/')
            else:
                session['user_id'] = result[0]['id']
                session['name'] = result[0]['first_name']
                return redirect('/home')
        else:
            flash("incorrect email and/or password")

    return redirect ('/')

@app.route('/on_logout')  
def on_logout():
    session.clear() 
    return redirect('/')

@app.route('/become_admin')
def become_admin():
    if "user_id" not in session:
        return redirect('/')
    query = "SELECT * FROM users WHERE id = %(sid)s"
    data = {'sid': session['user_id']}
    mysql = connectToMySQL(schema)
    users = mysql.query_db(query,data)
    return render_template("become_admin.html", users = users)

@app.route('/admin_click/<user_id>', methods = ["POST"])
def admin_click(user_id):
    if "user_id" not in session:
        return redirect('/')

    #is_valid = True
    #if request.form['age'] < 23:
        #is_valid = False
        #flash("Admins must be 24 years old or older")
    #if is_valid:
    query = "UPDATE users SET admin = true, age = %(age)s, updated_at = NOW() WHERE id = %(uid)s"
    data = {'age':request.form['age'],'uid':user_id}
    mysql = connectToMySQL(schema)
    mysql.query_db(query, data)

    return redirect ('/create_home')

@app.route('/kid_click/<user_id>', methods = ["POST"])
def kid_click(user_id):
    if "user_id" not in session:
        return redirect('/')

    query = "UPDATE users SET admin = false, age = %(age)s, updated_at = NOW() WHERE id = %(uid)s"
    data = {'age':request.form['age'],'uid':user_id}
    mysql = connectToMySQL(schema)
    mysql.query_db(query, data)
    return redirect('/join_home')

@app.route('/create_home')
def create_home():
    if "user_id" not in session:
        return redirect('/')
    query = "SELECT * FROM users WHERE id = %(sid)s AND admin = true"
    data = {'sid': session['user_id']}
    mysql = connectToMySQL(schema)
    admins = mysql.query_db(query,data)
    return render_template('create_home.html', admins = admins)

@app.route('/on_create_home', methods=['POST'])
def on_create_home():
    is_valid = True

    if len(request.form['hn']) < 3:
        is_valid=False
        flash("house name must be atleast 3 characters long.")
    if len(request.form['pw']) < 7:
        is_valid=False
        flash("password must be atleast 7 characters long.")
    if request.form['pw'] != request.form['cpw']:
        is_valid=False
        flash("Passwords must match")
    if is_valid:
        query = "INSERT INTO homes(user_id, home_name, home_pw, created_at, updated_at) VALUES (%(sid)s, %(hn)s, %(hpw)s, NOW(), NOW())"
        data = {
            'sid':session['user_id'],
            'hn':request.form['hn'],
            "hpw": bcrypt.generate_password_hash(request.form['pw'])
        }
        mysql = connectToMySQL(schema)
        mysql.query_db(query,data)
        return redirect('/join_home')
    return redirect('/create_home')

@app.route('/join_home')
def join_home():
    if "user_id" not in session:
        return redirect('/')
    
    return render_template('join_home.html')

@app.route('/on_join_home', methods=["POST"])
def on_join_home():
    is_valid = True
    if is_valid:
        query = "SELECT * FROM homes WHERE home_name = %(hn)s"
        data = {
            'hn': request.form['hn']
        } 
        mysql = connectToMySQL(schema)
        result = mysql.query_db(query, data)
        if result:
            if not bcrypt.check_password_hash(result[0]['home_pw'], request.form['pw']):
                flash("incorrect password and/or Home Name")
                return redirect('/join_home')
            else:
                #cant figure out how to add user to home
                print(session['user_id'])
                
                return redirect('/find_home')
        else:
            flash("incorrect email and/or password")
    return redirect ('/join_home')

@app.route('/find_home')
def find_home():
    if "user_id" not in session:
        return redirect('/')
    query = "select * from homes JOIN users on homes.user_id = users.id"
    mysql = connectToMySQL(schema)
    homes = mysql.query_db(query)

    query = "SELECT * FROM users WHERE id = %(sid)s AND has_home = false"
    data = {'sid': session['user_id']}
    mysql = connectToMySQL(schema)
    users_nothome = mysql.query_db(query,data)

    return render_template('find_home.html',homes=homes, users_nothome=users_nothome)

@app.route('/found_home/<home_id>')
def found_home(home_id):
    query = "UPDATE users SET has_home = true, updated_at = NOW() WHERE id = %(uid)s"
    data = {'uid':session['user_id']}
    mysql = connectToMySQL(schema)
    mysql.query_db(query, data)

    query = "INSERT INTO family(home_id, user_id, created_at, updated_at) VALUES(%(hid)s, %(sid)s, NOW(), NOW())"
    data = {
        'hid':home_id,
        'sid':session['user_id']
    }
    mysql = connectToMySQL(schema)
    mysql.query_db(query, data)
    return redirect('/home')

@app.route('/home')
def home():
    if "user_id" not in session:
        return redirect('/')
    query = "SELECT * FROM homes where user_id = %(sid)s"
    data = {'sid':session['user_id']}
    mysql = connectToMySQL(schema)
    homes = mysql.query_db(query, data)
    
    return render_template('home.html', homes=homes)

if __name__ == "__main__":
    app.run(debug=True)