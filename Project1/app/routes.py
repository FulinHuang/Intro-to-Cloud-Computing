from flask import render_template, url_for, redirect, flash, jsonify, make_response, request
from app import app, db
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, RegistrationForm, DeleteAccountForm, URLUploadPhotoForm, ChangePasswordForm
from app.user import User
from app.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email
from app.forms import ResetPasswordForm
from app.photo import Photo
import uuid
import os
import cv2
import urllib.request
from FaceMaskDetection.pytorch_infer import inference
from werkzeug.utils import secure_filename
from datetime import datetime

@app.route('/index')
@login_required
def index():
    now = datetime.now()  # current date and time
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
    all_files = []
    photo_noface = []
    photo_allmask = []
    photo_nomask = []
    photo_partmask = []
    photo_all = Photo.query.filter_by(username=current_user.get_username()).all()
    for photo in photo_all:
        all_files.append(photo.photourl)
        if photo.imagetype == 0:
            photo_noface.append(photo.photourl)
        elif photo.imagetype == 1:
            photo_allmask.append(photo.photourl)
        elif photo.imagetype == 2:
            photo_nomask.append(photo.photourl)
        else:
            photo_partmask.append(photo.photourl)
    return render_template('index.html', title='Home', all_files=all_files, photo_noface=photo_noface,
                           photo_allmask=photo_allmask, photo_nomask=photo_nomask, photo_partmask=photo_partmask, date_time =date_time )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.get_username() != 'admin':
            flash('Only Admin can register new account, please login if you are Admin')
            return redirect(url_for('login'))
        else:
            form = RegistrationForm()
            if form.validate_on_submit():
                user = User(username=form.username.data, email=form.email.data)
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                flash('Congratulations, you just registered a user!')
                return redirect(url_for('login'))
            return render_template('register.html', title='REGISTER', form=form)
    flash('Only Admin can register new account, please login first')
    return redirect(url_for('login'))


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if current_user.is_authenticated:
        form = ChangePasswordForm()
        if form.validate_on_submit():
            user = current_user
            if not user.check_password(form.old_password.data):
                flash('Your original password is incorrect')
                return render_template('change_password.html', title='CHANGE PASSWORD', form=form)
            user.set_password(form.new_password.data)
            db.session.add(user)
            db.session.commit()
            flash('You have changed your password, please re-login')
            logout_user()
            return redirect(url_for('login'))
        return render_template('change_password.html', title='CHANGE PASSWORD', form=form)


@app.route('/api/register', methods=['POST'])
def register_test():
    if request.method != 'POST':
        message = "Method not allowed"
        return jsonify({
            "success": False,
            "error": {
                "code": 405,
                "message": message
            }
        })

    user = request.form.get('username')
    password = request.form.get('password')
    if len(user) == 0 or len(password) == 0:
        return jsonify({
            "success": False,
            "error": {"code": 400,
                      "message": "At least one field is empty!"
                      }
        }
        )
    username = User.query.filter_by(username=user).first()
    if username:
        return jsonify({
            "success": False,
            "error": {"code": 400,
                      "message": "Username already exist!"
                      }
        }
        )

    user = User(username=user)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"success": True})


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if current_user.is_authenticated:
        user_list = [[]]
        user_parse = User.query.all()
        for usernames in user_parse:
            photo_count = 0
            photo_has = Photo.query.filter_by(username=usernames.get_username()).all()
            while photo_count < len(photo_has):
                photo_count = photo_count + 1
            user_list.append([usernames.get_username(), usernames.get_email(), photo_count])
        if current_user.get_username() != 'admin':
            flash('Only Admin can delete account, please login if you are Admin')
            return redirect(url_for('login'))
        else:
            form = DeleteAccountForm()
            if form.validate_on_submit():
                User.query.filter_by(username=form.username.data).delete()
                db.session.commit()
                flash('You have deleted an account successfully!')
                return redirect(url_for('index'))
            return render_template('delete_account.html', title='Delete_Account', form=form, user_list=user_list)
    flash('Only Admin can delete account, please login first')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='LOGIN', form=form)


@app.route('/index', methods=['POST'])
def upload():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    file_ext = os.path.splitext(filename)[1]
    filename = str(uuid.uuid4()) + file_ext
    if uploaded_file.filename != '':
        if file_ext not in app.config['UPLOAD_PHOTO_EXTENSIONS']:
            flash('Please choose a photo with correct format!')
            return redirect(url_for('index'))
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Success!')
    else:
        flash('Please select a file!')
        return redirect(url_for('index'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    num_face, num_mask, num_unmask = mask_detection(filepath, filename)

    flash('In this photo, we have detected {} faces: {} with masks on while {} without masks faces on.'.format(num_face,
                                                                                                               num_mask,
                                                                                                               num_unmask))

    return redirect(url_for('index'))


@app.route('/urlupload', methods=['GET', 'POST'])
def urlupload():
    form = URLUploadPhotoForm()
    if form.validate_on_submit():
        photourl = form.photoURL.data
        filename = photourl.split('/')[-1]
        filename = secure_filename(filename)
        file_ext = os.path.splitext(filename)[1]
        filename = str(uuid.uuid4()) + file_ext
        unique_file = filename
        if filename != '':
            if file_ext in app.config['UPLOAD_PHOTO_EXTENSIONS']:
                opener = urllib.request.URLopener()
                filename, headers = opener.retrieve(photourl, os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('Success!')

                num_face, num_mask, num_unmask = mask_detection(filename, unique_file)

                flash(
                    'In this photo, we have detected {} faces: {} with masks on while {} without masks faces on.'.format(
                        num_face, num_mask, num_unmask))
                return redirect(url_for('index'))
            flash('Please submit a photo with correct format!')
        else:
            flash('Empty file!')
    return render_template('urlupload.html', form=form)


@app.route('/api/upload', methods=['POST'])
def upload_test():
    if request.method != 'POST':
        message = "Method not allowed"
        return jsonify({
            "success": False,
            "error": {
                "code": 405,
                "message": message
            }
        })

    user = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=user).first()
    if user is None or not user.check_password(password):
        message = "Invalid username or password!"
        return jsonify({
            "success": False,
            "error": {
                "code": 400,
                "message": message
            }
        })

    login_user(user)
    if 'file' not in request.files:
        message = "No file selected!"
        return jsonify({
            "success": False,
            "error": {
                "code": 400,
                "message": message
            }
        })

    file = request.files['file']
    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1]
    filename = str(uuid.uuid4()) + file_ext
    if filename == '':
        message = "No file selected!"
        return jsonify({
            "success": False,
            "error": {
                "code": 400,
                "message": message
            }
        })

    if filename:
        if file_ext not in app.config['UPLOAD_PHOTO_EXTENSIONS']:
            message = "File type not supported!"
            return jsonify({
                "success": False,
                "error": {
                    "code": 400,
                    "message": message
                }
            })

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        num_face, num_mask, num_unmask = mask_detection(filepath, filename)
        return jsonify(
            {
                "success": True,
                "payload": {
                    "num_faces": num_face,
                    "num_masked": num_mask,
                    "num_unmasked": num_unmask
                }
            })


def mask_detection(filename, unique_file):
    img = cv2.imread(filename)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    output_info, output_image = inference(img, show_result=False, target_shape=(360, 360))
    output_image.save(os.path.join(app.config['OUTPUT_FOLDER'], unique_file), 'JPEG')

    num_mask = 0
    num_unmask = 0
    num_face = len(output_info)

    for i in range(num_face):
        if output_info[i][0] == 0:
            num_mask += 1
        else:
            num_unmask += 1
    if num_face == 0:
        image_type = 0
    elif num_face == num_mask:
        image_type = 1
    elif num_face == num_unmask:
        image_type = 2
    else:
        image_type = 3

    u = Photo(username=current_user.username, photourl=unique_file, imagetype=image_type)

    db.session.add(u)
    db.session.commit()

    return num_face, num_mask, num_unmask
