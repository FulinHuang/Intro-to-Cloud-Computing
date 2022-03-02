import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ece1779'
    SQLALCHEMY_DATABASE_URI = 'path'
    # SQLALCHEMY_DATABASE_URI = 'path'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'ece1779allen@gmail.com'
    MAIL_PASSWORD = 'doubanjiang'
    ADMINS = ['ece1779@gmail.com']
    POSTS_PER_PAGE = 25
    UPLOAD_FOLDER = basedir + '/static/image'
    OUTPUT_FOLDER = basedir + '/static/output'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # prevent large file size
    UPLOAD_PHOTO_EXTENSIONS = ['.JPG', '.jpg', '.PNG', '.png', '.GIF', '.gif', '.JPEG', '.jpeg', 'TIFF', 'tiff', 'RAW', 'raw']
