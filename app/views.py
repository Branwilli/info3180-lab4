import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, current_app, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm, UploadForm
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

###
# Routing for your application.
###
load_dotenv()

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    form = UploadForm()
    # Instantiate your form class
    if request.method == "POST" and form.validate_on_submit():
        file = form.file.data
            # Get file data and save to your uploads folder
        if file and allowed_files(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename)) # code is breaking here 

            flash('File Saved', category='success')
            return redirect(url_for('files'))  # Update this to redirect the user to a route that displays all uploaded image files'''
        flash("Upload Failed", category='error')
    return render_template('upload.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # change this to actually validate the entire form submission
    # and not just one field
    if  form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # Get the username and password values from the form.
        user = db.session.execute(db.select(UserProfile).filter_by(username=username)).scalar()
        
        if user and check_password_hash(user.password, password):
            # Gets user id, load into session
            login_user(user)

            # Remember to flash a message to the user
            #return redirect(url_for("home"))  # The user should be redirected to the upload form instead

            flash("Login succesful", category="success")
            return redirect(url_for("upload"))
        else:
            flash("Invalid username or password", category="error")
            return redirect(url_for('login'))
        
        # Using your model, query database for a user based on the username
        # and password submitted. Remember you need to compare the password hash.
        # You will need to import the appropriate function to do so.
        # Then store the result of that query to a `user` variable so it can be
        # passed to the login_user() method below.

    return render_template("login.html", form=form)

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

@app.route("/uploads/<filename>")
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/files')
@login_required
def files():
    images = get_uploaded_images()
    return render_template('files.html', images=images)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('home'))
    
###
# The functions below should be applicable to all Flask apps.
###

ALLOWED_EXTENSIONS = {'png', 'jpg'}

def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_uploaded_images():
    uploaded_images = []
    upload_folder = os.path.join(os.getcwd(), 'uploads')

    if not os.path.exists(upload_folder):
        return uploaded_images
    
    for subdir, dirs, files in os.walk(upload_folder):
        for file in files:
            if file.lower().endswith(('png', 'jpg')):
                uploaded_images.append(file)

    return uploaded_images

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
