import inspect
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, session
from ..manager.query import QueryManager
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from ..manager.models import AppUser
from functools import wraps

app = Flask(__name__)
app.debug = True

query = QueryManager()


def jsonify_results(query_method):
    method_parameters = inspect.signature(query_method).parameters.keys()
    request_dict = {k: v for k, v in request.args.items() if k in method_parameters}
    return jsonify(query_method(**request_dict))


@app.route("/")
def index():
    return render_template('home.html')


# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, please login', 'danger')
            return redirect(url_for('login'))
    return wrap


# About
@app.route('/about')
def about():
    return render_template('about.html')


# Register form class
class RegisterForm(Form):
    name = StringField(u'Name', [validators.Length(min=3, max=50)])
    username = StringField(u'User Name', [validators.Length(min=4, max=25)])
    email = StringField(u'Email', [validators.Length(min=6, max=50)])
    password = PasswordField(u'Password', [
        validators.data_required(),
        validators.equal_to('confirm', message='Password do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():

        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # insert
        query.session.add(AppUser(name=name, email=email, username=username, password=password))
        query.session.flush()

        flash('You are now registered and can login', 'success')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('Logged out!', 'success')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        # get user by username
        user = query.session.query(AppUser).filter(AppUser.username == username).one_or_none()

        if user:
            if sha256_crypt.verify(password_candidate, user.password):
                app.logger.info('PASSWORD matched')
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in!', 'success')

                return redirect(url_for('dashboard'))
            else:
                app.logger.info('PASSWORD NOT matched')
                error = 'Invalid login'
                return render_template('login.html', error=error)
        else:
            app.logger.info('Username not found')
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # create cursor
    entries = query.get_entry(limit=10)

    if len(entries) > 0:
        return render_template('dashboard.html', entries=entries)
    else:
        msg = 'No articles found'
        return render_template('dashboard.html', msg=msg)


@app.route("/api/keywords/")
def keywords():
    return jsonify(query.keywords)


@app.route('/api/tissues_in_references/')
def tissues_in_references():
    return jsonify(query.tissues_in_references)


@app.route('/api/subcellular_locations/')
def subcellular_locations():
    return jsonify(query.subcellular_locations)


@app.route('/api/taxids/')
def taxids():
    return jsonify(query.taxids)


@app.route('/api/dbreference_types/')
def dbreference_types():
    return jsonify(query.dbreference_types)


@app.route("/api/get_entry/")
def get_entry():
    return jsonify_results(query.get_entry)


@app.route("/api/get_disease/")
def get_disease():
    return jsonify_results(query.get_disease)


@app.route("/api/get_disease_comment/")
def get_get_disease_comment():
    return jsonify_results(query.get_disease_comment)


@app.route("/api/get_alternative_full_name/")
def get_alternative_full_name():
    return jsonify_results(query.get_alternative_full_name)


@app.route("/api/get_alternative_short_name/")
def get_alternative_short_name():
    return jsonify_results(query.get_alternative_short_name)


@app.route('/api/get_accession/')
def get_accession():
    return jsonify_results(query.get_accession)


@app.route("/api/get_pmid/")
def get_pmid():
    return jsonify_results(query.get_pmid)


@app.route("/api/get_organismHost/")
def get_organismHost():
    return jsonify_results(query.get_organismHost)


@app.route("/api/get_dbReference/")
def get_dbReference():
    return jsonify_results(query.get_dbReference)


@app.route("/api/get_feature/")
def get_feature():
    return jsonify_results(query.get_feature)


@app.route("/api/get_function/")
def get_function():
    return jsonify_results(query.get_function)


@app.route("/api/get_keyword/")
def get_keyword():
    return jsonify_results(query.get_keyword)


@app.route("/api/get_ec_number/")
def get_ec_number():
    return jsonify_results(query.get_ec_number)


@app.route("/api/get_subcellular_location/")
def get_subcellular_location():
    return jsonify_results(query.get_subcellular_location)


@app.route("/api/get_tissue_specificity/")
def get_tissue_specificity():
    return jsonify_results(query.get_tissue_specificity)


@app.route("/api/get_tissue_in_reference/")
def get_tissue_in_reference():
    return jsonify_results(query.get_tissue_in_reference)


def get_app():
    app.secret_key = 'sdjfgaksjf326742b45uztcfq'
    return app
