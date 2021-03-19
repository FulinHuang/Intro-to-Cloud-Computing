from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

instance_start_time = time.time()
from app import routes
from app import manager
from app import auto_scaler
