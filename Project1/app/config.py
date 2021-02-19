import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ece1779'
    SQLALCHEMY_DATABASE_URI = 'mysql://ece1779:ece1779project1@ece1779-a1.cbqorhddlq5b.us-east-1.rds.amazonaws.com/ece1779a1'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'lu19920218@gmail.com'
    MAIL_PASSWORD = 'Lfar13196'
    ADMINS = ['lu19920218@gmail.com']
    POSTS_PER_PAGE = 25
    UPLOAD_FOLDER = basedir + '/static/image'
    OUTPUT_FOLDER = basedir + '/static/output'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # prevent large file size
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif', '.jpeg', '.JPEG', '.PNG', '.JPG', '.GIF']