from flasgger import Swagger
from functools import wraps
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, session
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from ..manager.models import AppUser
from ..manager.query import QueryManager

app = Flask(__name__)

app.debug = True

app.config.setdefault('SWAGGER', {
    'title': 'PyUniProt Web API',
    'description': 'This exposes the functions of PyUniProt as a RESTful API',
    'contact': {
        'responsibleOrganization': 'Fraunhofer SCAI',
        'responsibleDeveloper': 'Christian Ebeling',
        'email': 'christian.ebeling@scai.fraunhofer.de',
        'url': 'https://www.scai.fraunhofer.de/de/geschaeftsfelder/bioinformatik.html',
    },
    'version': '0.1.0',
})

swagger = Swagger(app)
query = QueryManager()


def get_args(request_args, allowed_int_args=[], allowed_str_args=[]):
    """Check allowed argument names and return is as dictionary"""
    args = {}

    for allowed_int_arg in allowed_int_args:
        int_value = request_args.get(allowed_int_arg, default=None, type=None)
        if int_value:
            args[allowed_int_arg] = int(int_value)

    for allowed_str_arg in allowed_str_args:
        str_value = request_args.get(allowed_str_arg, default=None, type=None)
        if str_value:
            args[allowed_str_arg] = str_value

    return args


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
    entries = query.entry(limit=10)

    if len(entries) > 0:
        return render_template('dashboard.html', entries=entries)
    else:
        msg = 'No articles found'
        return render_template('dashboard.html', msg=msg)


@app.route("/api/property/keywords/", methods=['GET', 'POST'])
def keywords():
    """
    Returns list of distinct UniProt keywords
    ---
    tags:
      - Properties
    """
    return jsonify(query.keywords)


@app.route('/api/property/tissues_in_references/', methods=['GET', 'POST'])
def tissues_in_references():
    """
    Returns list of distinct UniProt tissues in references
    ---
    tags:
      - Properties
    """
    return jsonify(query.tissues_in_references)


@app.route('/api/property/subcellular_locations/', methods=['GET', 'POST'])
def subcellular_locations():
    """
    Returns list of distinct UniProt tissues in references
    ---
    tags:
      - Properties
    """
    return jsonify(query.subcellular_locations)


@app.route('/api/property/taxids/', methods=['GET', 'POST'])
def taxids():
    """
    Returns list of distinct UniProt subcellular locations
    ---
    tags:
      - Properties
    """
    return jsonify(query.taxids)


@app.route('/api/property/dbreference_types/', methods=['GET', 'POST'])
def dbreference_types():
    """
    Returns list of distinct UniProt dbreference types
    ---
    tags:
      - Properties
    """
    return jsonify(query.dbreference_types)


@app.route("/api/query/entry/", methods=['GET', 'POST'])
def query_entry():
    """
    Returns list of UniProt entries by query paramaters
    ---

    tags:

      - Query functions

    parameters:

      - name: dataset
        in: query
        type: string
        enum: ['Swiss-Prot', 'TrEMBL']
        required: false
        default: Swiss-Prot

      - name: name
        in: query
        type: string
        required: false
        description: test
        default: 1433E_HUMAN

      - name: recommended_full_name
        in: query
        type: string
        required: false
        default: 14-3-3 protein epsilon

      - name: recommended_short_name
        in: query
        type: string
        required: false
        default: 14-3-3E

      - name: gene_name
        in: query
        type: string
        required: false
        default: YWHAE

      - name: sequence
        in: query
        type: string
        required: false
        default: '%KLAEQAER%'

      - name: accession
        in: query
        type: string
        required: false
        default: P62258

      - name: organism_host
        in: query
        type: string
        required: false

      - name: feature_type
        in: query
        type: string
        required: false
        default: 'splice variant'

      - name: function_
        in: query
        type: string
        required: false
        default: '%Positively regulates%'

      - name: ec_number
        in: query
        type: string
        required: false

      - name: db_reference
        in: query
        type: string
        required: false
        default: 'GO:0021766'

      - name: alternative_full_name
        in: query
        type: string
        required: false

      - name: alternative_short_name
        in: query
        type: string
        required: false

      - name: disease_comment
        in: query
        type: string
        required: false

      - name: disease_name
        in: query
        type: string
        required: false

      - name: tissue_specificity
        in: query
        type: string
        required: false

      - name: other_gene_name
        in: query
        type: string
        required: false

      - name: taxid
        in: query
        type: integer
        required: false
        description: NCBI taxonomy identifier
        default: 9606

      - name: pmid
        in: query
        type: integer
        required: false
        default: 7644510

      - name: limit
        in: query
        type: integer
        required: false
        default: 1
    """
    args = {}

    if request.method == 'GET':

        allowed_str_args = ['dataset', 'name', 'recommended_full_name', 'feature_type', 'disease_name',
                            'recommended_short_name', 'gene_name', 'sequence', 'accession', 'organism_host',
                            'feature_type', 'function_', 'ec_number', 'db_reference', 'alternative_full_name',
                            'alternative_short_name', 'disease_comment', 'tissue_specificity', 'other_gene_name']

        allowed_int_args = ['taxid', 'limit', 'id', 'pmids']

        args = get_args(
            request_args=request.args,
            allowed_int_args=allowed_int_args,
            allowed_str_args=allowed_str_args
        )
        print(args)

    return jsonify(query.entry(**args))


@app.route("/api/query/disease/", methods=['GET', 'POST'])
def query_disease():
    """
    Returns list of diseases by query parameters
    ---

    tags:

      - Query functions

    parameters:

      - name: identifier
        in: query
        type: string
        required: false
        description: Disease identifier
        default: DI-03832

      - name: ref_id
        in: query
        type: string
        required: false
        description: reference identifier
        default: 104300

      - name: ref_type
        in: query
        type: string
        required: false
        description: Reference type
        default: MIM

      - name: name
        in: query
        type: string
        required: false
        description: Disease name
        default: Alzheimer disease

      - name: acronym
        in: query
        type: string
        required: false
        description: Disease acronym
        default: AD

      - name: description
        in: query
        type: string
        required: false
        description: Description of disease
        default: '%neurodegenerative disorder%'

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """
    args = {}

    if request.method == 'GET':

        allowed_str_args = ['identifier', 'ref_id', 'ref_type', 'name', 'acronym', 'description']

        args = get_args(
            request_args=request.args,
            allowed_str_args=allowed_str_args
        )

    return jsonify(query.disease(**args))


@app.route("/api/query/alternative_full_name/", methods=['GET', 'POST'])
def query_alternative_full_name():
    """
    Returns list of alternative full name by query query parameters
    ---
    tags:

      - Query functions

    parameters:

      - name: name
        in: query
        type: string
        required: false
        description: Alternative full name
        default: 'Alzheimer disease amyloid protein'

      - name: entry_name
        in: query
        type: string
        required: false
        description: UniProt entry name
        default: A4_HUMAN

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """

    args = get_args(
        request_args=request.args,
        allowed_str_args=['name', 'entry_name'],
        allowed_int_args=['limit']
    )

    return jsonify(query.alternative_full_name(**args))


@app.route("/api/query/alternative_short_name/", methods=['GET', 'POST'])
def query_alternative_short_name():
    """
    Returns list of alternative short name by query query parameters
    ---

    tags:

      - Query functions

    parameters:

      - name: name
        in: query
        type: string
        required: false
        description: Alternative short name
        default: CVAP

      - name: entry_name
        in: query
        type: string
        required: false
        description: UniProt entry name
        default: A4_HUMAN

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """

    args = get_args(
        request_args=request.args,
        allowed_str_args=['name', 'entry_name'],
        allowed_int_args=['limit']
    )

    return jsonify(query.alternative_short_name(**args))


@app.route("/api/query/other_gene_name/", methods=['GET', 'POST'])
def query_other_gene_name():
    """
    Returns list of alternative short name by query query parameters
    ---

    tags:

      - Query functions

    parameters:

      - name: type_
        in: query
        type: string
        required: false
        description: Alternative short name
        default: CVAP

      - name: name
        in: query
        type: string
        required: false
        description: Alternative short name
        default: CVAP

      - name: entry_name
        in: query
        type: string
        required: false
        description: UniProt entry name
        default: A4_HUMAN

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """

    args = get_args(
        request_args=request.args,
        allowed_str_args=['name', 'entry_name'],
        allowed_int_args=['limit']
    )

    return jsonify(query.other_gene_name(**args))


@app.route('/api/query/accession/', methods=['GET', 'POST'])
def query_accession():
    """
    Returns list of accession numbers by query query parameters
    ---

    tags:

      - Query functions

    parameters:

      - name: accession
        in: query
        type: string
        required: false
        description: UniProt accession number
        default: P05067

      - name: entry_name
        in: query
        type: string
        required: false
        description: UniProt entry name
        default: A4_HUMAN

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """

    args = get_args(
        request_args=request.args,
        allowed_str_args=['accession', 'entry_name'],
        allowed_int_args=['limit']
    )

    return jsonify(query.accession(**args))


@app.route("/api/query/pmid/", methods=['GET', 'POST'])
def query_pmid():
    """
    Returns list of PubMed identifier by query parameters
    ---

    tags:

      - Query functions

    parameters:

      - name: pmid
        in: query
        type: string
        required: false
        description: PubMed identifier
        default: 20697050

      - name: entry_name
        in: query
        type: string
        required: false
        description: UniProt entry name
        default: A4_HUMAN

      - name: first
        in: query
        type: string
        required: false
        description: first page
        default: 987

      - name: last
        in: query
        type: string
        required: false
        description: last page
        default: 995

      - name: volume
        in: query
        type: string
        required: false
        description: Volume
        default: 67

      - name: name
        in: query
        type: string
        required: false
        description: Name of journal
        default: 'Arch. Neurol.'

      - name: date
        in: query
        type: string
        required: false
        description: Publication date
        default: 2010

      - name: title
        in: query
        type: string
        required: false
        description: Title of publication
        default: '%amyloidosis%'

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """
    args = get_args(
        request_args=request.args,
        allowed_str_args=['first', 'last', 'volume', 'name', 'date', 'title', 'entry_name'],
        allowed_int_args=['pmid', 'limit']
    )

    return jsonify(query.pmid(**args))


@app.route("/api/query/organism_host/", methods=['GET', 'POST'])
def query_organism_host():
    """
    Returns list of host organism by query parameters
    ---

    tags:

      - Query functions

    parameters:

      - name: taxid
        in: query
        type: integer
        required: false
        description: NCBI taxonomy identifier
        default: 9606

      - name: entry_name
        in: query
        type: string
        required: false
        description: UniProt entry name
        default: A4_HUMAN

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """
    args = get_args(
        request_args=request.args,
        allowed_str_args=['entry_name'],
        allowed_int_args=['taxid', 'limit']
    )

    return jsonify(query.organism_host(**args))


@app.route("/api/query/db_reference/", methods=['GET', 'POST'])
def query_db_reference():
    """
    Returns list of cross references by query parameters
    ---

    tags:

      - Query functions

    parameters:

      - name: type_
        in: query
        type: string
        required: false
        description: Reference type
        default: EMBL

      - name: identifier
        in: query
        type: string
        required: false
        description: reference identifier
        default: Y00264

      - name: entry_name
        in: query
        type: string
        required: false
        description: UniProt entry name
        default: A4_HUMAN

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """
    args = get_args(
        request_args=request.args,
        allowed_str_args=['type_', 'identifier', 'entry_name'],
        allowed_int_args=['limit']
    )

    return jsonify(query.db_reference(**args))


@app.route("/api/query/feature/", methods=['GET', 'POST'])
def query_feature():
    """
    Returns list of sequence feature by query parameters
    ---
    tags:

      - Query functions

    parameters:

      - name: type_
        in: query
        type: string
        required: false
        description: Feature type
        default: 'splice variant'

      - name: identifier
        in: query
        type: string
        required: false
        description: Feature identifier
        default: VSP_045447

      - name: description
        in: query
        type: string
        required: false
        description: Feature description
        default: 'In isoform 11.'

      - name: entry_name
        in: query
        type: string
        required: false
        description: UniProt entry name
        default: A4_HUMAN

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """
    args = get_args(
        request_args=request.args,
        allowed_str_args=['type_', 'identifier', 'entry_name'],
        allowed_int_args=['limit']
    )

    return jsonify(query.feature(**args))


@app.route("/api/query/function/", methods=['GET', 'POST'])
def query_function():
    """
    Returns list of functions by query parameters
    ---
    tags:

      - Query functions

    parameters:

      - name: text
        in: query
        type: string
        required: false
        description: Text describing protein function
        default: '%axonogenesis%'

      - name: entry_name
        in: query
        type: string
        required: false
        description: UniProt entry name
        default: A4_HUMAN

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """
    args = get_args(
        request_args=request.args,
        allowed_str_args=['text', 'entry_name'],
        allowed_int_args=['limit']
    )

    return jsonify(query.function(**args))


@app.route("/api/query/keyword/", methods=['GET', 'POST'])
def query_keyword():
    """
    Returns list of keywords linked to entries by query parameters
    ---
    tags:

      - Query functions

    parameters:

      - name: name
        in: query
        type: string
        required: false
        description: Disease identifier
        default: 'Ubl conjugation'

      - name: identifier
        in: query
        type: string
        required: false
        description: Disease identifier
        default: KW-0832

      - name: entry_name
        in: query
        type: string
        required: false
        description: reference identifier
        default: A4_HUMAN

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """
    args = get_args(
        request_args=request.args,
        allowed_str_args=['name', 'identifier', 'entry_name'],
        allowed_int_args=['limit']
    )

    print(args)

    return jsonify(query.keyword(**args))


@app.route("/api/query/ec_number/", methods=['GET', 'POST'])
def query_ec_number():
    """
    Returns list of Enzyme Commission Numbers (EC numbers) by query parameters
    ---
    tags:

      - Query functions

    parameters:

      - name: ec_number
        in: query
        type: string
        required: false
        description: Enzyme Commission Number
        default: '1.1.1.1'

      - name: entry_name
        in: query
        type: string
        required: false
        description: UniProt entry name
        default: ADHX_HUMAN

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """
    args = get_args(
        request_args=request.args,
        allowed_str_args=['ec_number', 'entry_name'],
        allowed_int_args=['limit']
    )
    return jsonify(query.ec_number(**args))


@app.route("/api/query/subcellular_location/", methods=['GET', 'POST'])
def query_subcellular_location():
    """
    Returns list of subcellular locations by query parameters
    ---

    tags:
      - Query functions

    parameters:

      - name: location
        in: query
        type: string
        required: false
        description: Subcellular location
        default: 'Clathrin-coated pit'

      - name: entry_name
        in: query
        type: string
        required: false
        description: reference identifier
        default: A4_HUMAN

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """
    args = get_args(
        request_args=request.args,
        allowed_str_args=['location', 'entry_name'],
        allowed_int_args=['limit']
    )

    return jsonify(query.subcellular_location(**args))


@app.route("/api/query/tissue_specificity/", methods=['GET', 'POST'])
def query_tissue_specificity():
    """
    Returns list of tissue specificity by query parameters
    ---

    tags:

      - Query functions

    parameters:

      - name: comment
        in: query
        type: string
        required: false
        description: Comment to tissue specificity
        default: '%APP695%'

      - name: entry_name
        in: query
        type: string
        required: false
        description: reference identifier
        default: A4_HUMAN

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """
    args = get_args(
        request_args=request.args,
        allowed_str_args=['comment', 'entry_name'],
        allowed_int_args=['limit']
    )

    return jsonify(query.tissue_specificity(**args))


@app.route("/api/query/tissue_in_reference/", methods=['GET', 'POST'])
def query_tissue_in_reference():
    """
    Returns list of tissues linked to references by query parameters
    ---

    tags:

      - Query functions

    parameters:
      - name: tissue
        in: query
        type: string
        required: false
        description: Tissue
        default: brain

      - name: entry_name
        in: query
        type: string
        required: false
        description: UniProt entry name
        default: A4_HUMAN

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 1
    """
    args = get_args(
        request_args=request.args,
        allowed_str_args=['tissue', 'entry_name'],
        allowed_int_args=['limit']
    )

    return jsonify(query.tissue_in_reference(**args))


@app.route("/api/query/disease_comment/", methods=['GET', 'POST'])
def query_disease_comment():
    """
    Returns list of diseases comments by query parameters
    ---

    tags:

      - Query functions

    parameters:

      - name: comment
        in: query
        type: string
        required: false
        description: Comment on disease linked to UniProt entry
        default: '%mutations%'

      - name: entry_name
        in: query
        type: string
        required: false
        description: reference identifier
        default: A4_HUMAN

      - name: limit
        in: query
        type: integer
        required: false
        description: limit of results numbers
        default: 10
    """
    args = get_args(
        request_args=request.args,
        allowed_str_args=['comment', 'entry_name'],
        allowed_int_args=['limit']
    )
    return jsonify(query.disease_comment(**args))


def get_app():
    app.secret_key = 'sdjfgaksjf326742b45uztcfq'
    return app
