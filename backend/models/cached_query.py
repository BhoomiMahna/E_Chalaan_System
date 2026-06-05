from .violation import db
from datetime import datetime

class CachedQuery(db.Model):
    __tablename__ = 'cached_queries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    query_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    query_text = db.Column(db.Text, nullable=True)
    sql_query = db.Column(db.Text, nullable=True)
    results_json = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
