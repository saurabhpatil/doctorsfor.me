from flask import render_template, flash, redirect, url_for, session, request
from app import app, con, mdb
from .forms import LoginForm
# from .forms import SignupForm
import hashlib


@app.route('/')
@app.route('/index')
def index():
    if not session.get('logged_in', False):
        return redirect('/login')
    user = {'username':'aditya'}
    posts = [
        {
            'author':{'nickname':'Alok'},
            'body':'Beautiful day in college station!'
        },
        {
            'author':{'nickname':'Atif'},
            'body':'Beautiful day in Austin!'
        }
    ]
    return render_template('index.html',title="Better Doctors For Me", user=user, posts=posts)

@app.route('/login', methods=['GET','POST'])
def login():
    if session.get('logged_in', False):
        return redirect(url_for('index'))
    form = LoginForm()
    if request.method == 'POST':
        error = None
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            # h = hashlib.sha1()
            # password = form.password.data
            # h.update(password)
            # password_hash = h.hexdigest()
            if username and password:
                sql_query = 'SELECT username FROM user_profile WHERE username="%s" AND password="%s"' % (username, password)
                cursor = con.cursor()
                cursor.execute(sql_query)
                data = cursor.fetchone()
                if data is not None:
                    session['logged_in'] = True
                    session['username'] = username
                    return redirect(request.args.get('next') or url_for('index'))
                else:
                    error = "No user could be found"
            error = "Invalid username/password combination"
            flash(error)
    return render_template('login.html',title='Sign In',form=form)

# @app.route('/signup', methods=['GET','POST'])
# def signup():
#     form = SignupForm()
#     if request.method == "POST":
#         error = None
#         print('Starting signup')
#         if form.validate_on_submit():
#             print('Form validated')
#             username = form.username.data
#             h = hashlib.sha1()
#             password = form.password.data
#             h.update(password)
#             password_hash = h.hexdigest()
#             first_name = form.firstname.data
#             last_name = form.lastname.data
#             email = form.emailid.data
#             unique_hash = "12345"
#             status = 0
#             cursor = con.cursor()
#             sql_query = 'SELECT username FROM User WHERE userName="%s"' % (username)
#             cursor.execute(sql_query)
#             data = cursor.fetchone()
#             if data is None:
#                 # Log user in and create account
#                 insert_query = 'INSERT INTO User(userName, password,firstName,lastName,emailID, hash, accountStatus) VALUES ("%s","%s","%s","%s","%s","%s","%s")' % (username, password_hash, first_name,last_name, email, unique_hash, status)
#                 cursor.execute(insert_query)
#                 con.commit()
#                 session['logged_in'] = True
#                 session['username'] = username
#                 return redirect(request.args.get('next') or url_for('index'))
#             else:
#                 error = "Sorry, username already taken"
#             flash(error)
#     return render_template('signup.html',title='Sign Up',form=form)
#     # except mdb.Error as e:
#     #     if con:
#     #         con.rollback()
#     #     print(e)   


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out.')
    return redirect('/')

@app.route('/user/<username>', methods=['GET','POST'])
def user(username):
    pass

@app.route('/search', methods=['GET','POST'])
def search():
    pass

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


