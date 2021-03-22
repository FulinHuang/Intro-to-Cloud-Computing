import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ece1779'

    # RDS database
    # SQLALCHEMY_DATABASE_URI = 'mysql://ece1779:ece1779project1@ece1779-a1.cbqorhddlq5b.us-east-1.rds.amazonaws.com/ece1779a1'
    # SQLALCHEMY_DATABASE_URI = 'mysql://allen_admin:lu19920218@allen-ece1779-a1.c7mezzt0p0rf.us-east-1.rds.amazonaws.com/dbname'
    SQLALCHEMY_DATABASE_URI = 'mysql://admin:ece1779pass@database-ece1779.cpng8nm7nagd.us-east-1.rds.amazonaws.com/userapp'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'ece1779allen@gmail.com'
    MAIL_PASSWORD = 'doubanjiang'
    ADMINS = ['ece1779@gmail.com']
    POSTS_PER_PAGE = 25

    # photo storage (LOCAL)
    UPLOAD_FOLDER = basedir + '/static/image'
    OUTPUT_FOLDER = basedir + '/static/output'

    # photo storage (AWS S3)
    BUCKET_NAME = 'ece1779yw'
    BUCKET_UPLOAD_FOLDER = 'image'
    BUCKET_OUTPUT_FOLDER = 'output'
    BUCKET_THUMBNAILS_FOLDER = 'thumbnails'
    # photo access (AWS S3)
    BUCKET_ADDRESS = 'https://ece1779yw.s3.amazonaws.com/'

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # prevent large file size
    UPLOAD_PHOTO_EXTENSIONS = ['.JPG', '.jpg', '.PNG', '.png', '.GIF', '.gif', '.JPEG', '.jpeg', 'TIFF', 'tiff', 'RAW', 'raw']