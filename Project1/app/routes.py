from flask import render_template, url_for, redirect, flash
from app import app, db
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, RegistrationForm, DeleteAccountForm, URLUploadPhotoForm
from app.model import User
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


@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': '您'},
            'body': '大SB!'
        }
    ]

    return render_template('index.html', title='Home', posts=posts)

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


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    #    if current_user.is_authenticated:
    #        return redirect(url_for('index'))

    # ONLY Admin can implement the registration
    if current_user.get_id() != '1':  # get_id for Admin is 1
        flash('Only Admin can register new account, please login first')
        return redirect(url_for('login'))
    else:
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        return render_template('register.html', title='REGISTER', form=form)


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
    form = DeleteAccountForm()
    if form.validate_on_submit():
        User.query.filter_by(username=form.username.data, email=form.email.data).delete()
        db.session.commit()
        flash('You have deleted an account successfully!')
        return redirect(url_for('index'))
    return render_template('delete_account.html', title='Delete_Account', form=form)


@app.route('/', methods=['GET'])
@app.route('/main', methods=['GET'])
def main():
    return render_template("main.html")


@app.route('/urlupload', methods=['GET', 'POST'])
def urlupload():
    form = URLUploadPhotoForm()
    if form.validate_on_submit():
        photourl = form.photoURL.data
        print(photourl)
        filename = photourl.split('/')[-1]
        filename = secure_filename(filename)
        filename = str(uuid.uuid4()) + filename
        unique_file = filename
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext in app.config['UPLOAD_EXTENSIONS']:
                opener = urllib.request.URLopener()
                filename, headers = opener.retrieve(photourl, os.path.join('app/static/image', filename))
                flash('Successfully Submit!')

                img = cv2.imread(filename)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                output_info, output_image = inference(img, show_result=False, target_shape=(360, 360))
                output_image.save(os.path.join('app/static/output', unique_file), 'JPEG')

                num_face = 0
                num_mask = 0
                num_unmask = 0
                image_type = 0

## -------------COMMENTED OUT for now until MaskDetection is done

#        num_face = len(output_info)
#        for i in range(num_face):
#            if output_info[i][0] == 0:
#                num_mask += 1
#            else:
#                num_unmask += 1
#        if num_face == 0:
#            image_type = 0  # no face
#        elif num_face == num_mask:
#            image_type = 1  # all masked
#        elif num_face == num_unmask:
#            image_type = 2  # all unmasked
#        else:
#            image_type = 3  # some masked

## ------------------------------

        u = Photo(username=current_user.username, photourl=filename, imagetype=image_type)
        db.session.add(u)
        db.session.commit()
        flash('There are {} faces been detected, {} mask faces been detected, {} unmasked faces been detected.'.format(num_face, num_mask, num_unmask))
        return redirect(url_for('index'))
    return render_template('urlupload.html', form=form)
