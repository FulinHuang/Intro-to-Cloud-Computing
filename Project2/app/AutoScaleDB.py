from app import db


class AutoScaleDB(db.Model):
    __tablename__ = 'AutoScale'
    id = db.Column(db.Integer, primary_key=True)
    cpu_max = db.Column(db.Float)
    cpu_min = db.Column(db.Float)
    ratio_expand = db.Column(db.Float)
    ratio_shrink = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)

