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

@app.route('/register')
def register():
    return render_template("reg.html")

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
            return redirect ('/become_admin')

    return redirect('/register')

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
    query = "UPDATE users SET admin = true, kid = false, has_home = false, age = %(age)s, updated_at = NOW() WHERE id = %(uid)s"
    data = {'age':request.form['age'],'uid':user_id}
    mysql = connectToMySQL(schema)
    mysql.query_db(query, data)

    return redirect ('/create_home')

@app.route('/kid_click/<user_id>', methods = ["POST"])
def kid_click(user_id):
    if "user_id" not in session:
        return redirect('/')

    query = "UPDATE users SET kid = true, admin = false, has_home=false, age = %(age)s, updated_at = NOW() WHERE id = %(uid)s"
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
        query = "INSERT INTO homes(creator_id, home_name, home_pw, created_at, updated_at) VALUES (%(sid)s, %(hn)s, %(hpw)s, NOW(), NOW())"
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
    query = "select * from homes JOIN users on creator_id = users.id"
    mysql = connectToMySQL(schema)
    homes = mysql.query_db(query)

    # query = "SELECT * FROM users WHERE id = %(sid)s AND has_home = false"
    # data = {'sid': session['user_id']}
    # mysql = connectToMySQL(schema)
    # users_nothome = mysql.query_db(query,data)

    return render_template("find_home.html", homes = homes)

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

@app.route('/on_create_work/<home_id>', methods=['POST'])
def created_work(home_id):
    if "user_id" not in session:
        return redirect('/')

    is_valid = True
    if len(request.form['des']) < 3:
        is_valid = False
        flash("A task must consist of at least 3 characters!")
    if len(request.form['val']) < 1:
        is_valid = False
        flash("A task must be worth at least 1 Kid Coin!")
    if is_valid:
        query = "INSERT INTO jobs(user_id, home_id, description, value, task, completed, approved, created_at, updated_at) VALUES(%(uid)s, %(hid)s, %(des)s, %(val)s, true, false, false, NOW(), NOW())"
        data = {
            'uid':session['user_id'],
            'hid':home_id,
            'des':request.form['des'],
            'val':request.form['val']
        }
        mysql = connectToMySQL(schema)
        mysql.query_db(query,data)
        print(session['user_id'])
        print(home_id)
        return redirect(f'/user_home/{home_id}')
    return redirect('/home')

@app.route('/on_completed_work/<job_id>')
def kid_completed_work(job_id):
    print(job_id)
    query = " UPDATE jobs SET completed = true, completed_by = %(sid)s, updated_at = NOW() where id = %(jid)s"
    data ={
        'jid':job_id,
        'sid':session['user_id']
        }
    mysql = connectToMySQL(schema)
    mysql.query_db(query, data)
    return redirect('/home')

@app.route('/on_approved_work/<job_id>')
def admin_approved_work(job_id):
    print(job_id)
    print(session['user_id'])
    query = " UPDATE jobs SET approved = true, updated_at = NOW() where id = %(jid)s"
    data ={
        'jid':job_id
        }
    mysql = connectToMySQL(schema)
    mysql.query_db(query, data)
    return redirect('/home')

@app.route('/approvals/<home_id>')
def all_approvals(home_id):
    if "user_id" not in session:
        return redirect('/')
    query = "SELECT * FROM jobs where completed_by = %(sid)s AND completed = true AND approved = True order by updated_at desc LIMIT 10"
    data={
        'sid':session['user_id']
    }
    mysql = connectToMySQL(schema)
    completed = mysql.query_db(query, data)

    query = "Select * FROM family JOIN homes ON home_id = homes.id WHERE user_id = %(sid)s"
    data={
        'sid':session['user_id']
    }
    mysql = connectToMySQL(schema)
    links = mysql.query_db(query,data)

    return render_template('approvals.html', completed = completed, links = links)

@app.route('/on_denied_work/<job_id>')
def admin_denied_work(job_id):
    print(job_id)
    print(session['user_id'])
    query = " UPDATE jobs SET completed = false, updated_at = NOW() where id = %(jid)s"
    data ={
        'jid':job_id
        }
    mysql = connectToMySQL(schema)
    mysql.query_db(query, data)
    return redirect('/home')

@app.route('/on_deleted_work/<job_id>')
def admin_deleted_work(job_id):
    print(job_id)
    print(session['user_id'])
    query = " DELETE FROM jobs WHERE id = %(jid)s"
    data ={
        'jid':job_id
        }
    mysql = connectToMySQL(schema)
    mysql.query_db(query, data)
    return redirect('/home')

@app.route('/on_goals/<home_id>', methods=['POST'])
def on_goals(home_id):
    if "user_id" not in session:
        return redirect('/')

    is_valid = True
    if len(request.form['des']) < 3:
        is_valid = False
        flash("A Bonus must consist of at least 3 characters!")
    if len(request.form['val']) < 1:
        is_valid = False
        flash("A Bonus must be worth at least 1 Kid Coin!")
    if is_valid:
        query = "INSERT INTO jobs(user_id, home_id, description, value, goal, completed, approved, created_at, updated_at) VALUES(%(uid)s, %(hid)s, %(des)s, %(val)s, true, false, false, NOW(), NOW())"
        data = {
            'uid':session['user_id'],
            'hid':home_id,
            'des':request.form['des'],
            'val':request.form['val']
        }
        mysql = connectToMySQL(schema)
        mysql.query_db(query,data)
        print(session['user_id'])
        print(home_id)
        return redirect(f'/user_home_bonus/{home_id}')
    return redirect('/home')

@app.route('/on_fun/<home_id>', methods=['POST'])
def on_fun(home_id):
    if "user_id" not in session:
        return redirect('/')
        
    is_valid = True
    if len(request.form['des']) < 2:
        is_valid = False
        flash("Fun must consist of at least 2 characters!")
    if len(request.form['val']) < 1:
        is_valid = False
        flash("Fun must cost at least 1 Kid Coin!")
    if is_valid:
        query = "INSERT INTO jobs(user_id, home_id, description, value, fun, completed, approved, created_at, updated_at) VALUES(%(uid)s, %(hid)s, %(des)s, %(val)s, true, false, false, NOW(), NOW())"
        data = {
            'uid':session['user_id'],
            'hid':home_id,
            'des':request.form['des'],
            'val':request.form['val']
        }
        mysql = connectToMySQL(schema)
        mysql.query_db(query,data)
        print(session['user_id'])
        print(home_id)
        return redirect(f'/user_home_fun/{home_id}')
    return redirect('/home')

@app.route('/user_home_bonus/<home_id>')
def bonus_room(home_id):
    if "user_id" not in session:
        return redirect('/')
    
    query = "SELECT * FROM homes JOIN users ON creator_id = users.id JOIN family ON users.id = family.user_id WHERE users.id = %(sid)s"
    data = {'sid':session['user_id']}
    mysql = connectToMySQL(schema)
    homes = mysql.query_db(query, data)

    query = "SELECT * FROM jobs where home_id = %(hid)s AND completed = false AND goal = true order by updated_at desc"
    data={
        'hid':home_id
    }
    mysql = connectToMySQL(schema)
    jobs = mysql.query_db(query, data)

    query = "SELECT * FROM jobs where home_id = %(hid)s AND completed = true AND approved = false AND goal = true order by updated_at desc"
    data={
        'hid':home_id
    }
    mysql = connectToMySQL(schema)
    completed = mysql.query_db(query, data)

    query = "Select * FROM family JOIN homes ON home_id = homes.id WHERE user_id = %(sid)s"
    data={
        'sid':session['user_id']
    }
    mysql = connectToMySQL(schema)
    links = mysql.query_db(query,data)

    return render_template('user_home_bonus.html', homes = homes, jobs = jobs, completed = completed, links = links)

@app.route('/user_home_fun/<home_id>')
def fun_room(home_id):
    if "user_id" not in session:
        return redirect('/')

    query = "SELECT * FROM homes JOIN users ON creator_id = users.id JOIN family ON users.id = family.user_id WHERE users.id = %(sid)s"
    data = {'sid':session['user_id']}
    mysql = connectToMySQL(schema)
    homes = mysql.query_db(query, data)

    query = "SELECT * FROM jobs where home_id = %(hid)s AND completed = false AND fun = true order by updated_at desc"
    data={
        'hid':home_id
    }
    mysql = connectToMySQL(schema)
    jobs = mysql.query_db(query, data)

    query = "SELECT * FROM jobs where home_id = %(hid)s AND completed = true AND approved = false AND fun = true order by updated_at desc"
    data={
        'hid':home_id
    }
    mysql = connectToMySQL(schema)
    completed = mysql.query_db(query, data)

    query = "Select * FROM family JOIN homes ON home_id = homes.id WHERE user_id = %(sid)s"
    data={
        'sid':session['user_id']
    }
    mysql = connectToMySQL(schema)
    links = mysql.query_db(query,data)

    return render_template('user_home_fun.html', homes = homes, jobs = jobs, completed = completed, links = links)

@app.route('/home')
def home_account():
    if "user_id" not in session:
        return redirect('/')

    query = "SELECT * FROM homes JOIN users ON creator_id = users.id JOIN family ON users.id = family.user_id WHERE users.id = %(sid)s"
    data = {'sid':session['user_id']}
    mysql = connectToMySQL(schema)
    homes = mysql.query_db(query, data)

    # query = "SELECT * FROM users WHERE id = %(sid)s AND admin = true"
    # data = {'sid': session['user_id']}
    # mysql = connectToMySQL(schema)
    # admins = mysql.query_db(query,data)

    query = "Select * FROM family JOIN homes ON home_id = homes.id WHERE user_id = %(sid)s"
    data={
        'sid':session['user_id']
    }
    mysql = connectToMySQL(schema)
    users = mysql.query_db(query,data)

    query = "Select * FROM users WHERE id = %(sid)s AND kid = false"
    data={
        'sid':session['user_id']
    }
    mysql = connectToMySQL(schema)
    peeps = mysql.query_db(query,data)

    query = "Select * FROM users WHERE id = %(sid)s AND has_home = false"
    data={
        'sid':session['user_id']
    }
    mysql = connectToMySQL(schema)
    peeps2 = mysql.query_db(query,data)

    # query = "SELECT * FROM jobs where home_id = %(sid)s"
    # data={
    #     'sid':session['user_id']
    # }
    # mysql = connectToMySQL(schema)
    # jobs = mysql.query_db(query, data)
    query = "select first_name, last_name, sum(value) as kid_coins from jobs join users on completed_by = users.id WHERE users.id = %(sid)s AND completed = true AND approved = true GROUP BY completed_by"
    data={
        'sid':session['user_id']
    }
    mysql = connectToMySQL(schema)
    kids = mysql.query_db(query,data)

    query = "Select * FROM family JOIN homes ON home_id = homes.id WHERE user_id = %(sid)s"
    data={
        'sid':session['user_id']
    }
    mysql = connectToMySQL(schema)
    links = mysql.query_db(query,data)

    query = "SELECT * FROM jobs where completed_by = %(sid)s AND completed = true AND approved = false order by updated_at desc "
    data={
        'sid':session['user_id']
    }
    mysql = connectToMySQL(schema)
    completed = mysql.query_db(query, data)

    return render_template("home.html", homes = homes, users = users, kids = kids, peeps = peeps, peeps2 = peeps2, links = links, completed = completed)

@app.route('/user_home/<home_id>')
def user_home(home_id):
    if "user_id" not in session:
        return redirect('/')

    query = "Select * FROM family JOIN homes ON home_id = homes.id WHERE user_id = %(sid)s"
    data={
        'sid':session['user_id']
    }
    mysql = connectToMySQL(schema)
    users = mysql.query_db(query,data)

    query = "SELECT * FROM jobs where home_id = %(hid)s AND completed = false AND task = true order by updated_at desc"
    data={
        'hid':home_id
    }
    mysql = connectToMySQL(schema)
    jobs = mysql.query_db(query, data)

    query = "SELECT * FROM jobs where home_id = %(hid)s AND completed = true AND approved = false AND task = true order by updated_at desc"
    data={
        'hid':home_id
    }
    mysql = connectToMySQL(schema)
    completed = mysql.query_db(query, data)

    query = "SELECT * FROM homes JOIN users ON creator_id = users.id JOIN family ON users.id = family.user_id WHERE users.id = %(sid)s"
    data = {'sid':session['user_id']}
    mysql = connectToMySQL(schema)
    homes = mysql.query_db(query, data)

    query = "select first_name, last_name, sum(value) as kid_coins from jobs join users on completed_by = users.id WHERE home_id = %(hid)s AND completed = true AND approved = true GROUP BY completed_by"
    data = {'hid':home_id}
    mysql = connectToMySQL(schema)
    kids = mysql.query_db(query, data)

    query = "Select * FROM family JOIN homes ON home_id = homes.id WHERE user_id = %(sid)s"
    data={
        'sid':session['user_id']
    }
    mysql = connectToMySQL(schema)
    bonuses = mysql.query_db(query,data)

    return render_template('user_home.html', jobs = jobs, users = users, completed = completed, homes = homes, kids = kids, bonuses = bonuses)

if __name__ == "__main__":
    app.run(debug=True)