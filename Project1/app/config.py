import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'allen plays basketball'
 #   SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
 #       'sqlite:///' + os.path.join(basedir, 'app.db')
 #    SQLALCHEMY_DATABASE_URI = 'mysql://allen_admin:lu19920218@allen-ece1779-a1.c7mezzt0p0rf.us-east-1.rds.amazonaws.com/dbname'
    SQLALCHEMY_DATABASE_URI = 'mysql://ece1779:ece1779project1@ece1779-a1.cbqorhddlq5b.us-east-1.rds.amazonaws.com/ece1779a1'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'lu19920218@gmail.com'
    MAIL_PASSWORD = 'Lfar13196'
    ADMINS = ['lu19920218@gmail.com']
    POSTS_PER_PAGE = 25

    UPLOAD_FOLDER = basedir + '/static/images'
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif', '.jpeg', '.JPEG', '.PNG', '.JPG', '.GIF']