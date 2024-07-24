from db import db
from datetime import datetime
import pytz


class Sale(db.Model):
    """Sale table"""
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    product_quantity = db.Column(db.Integer, nullable=False)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(15))
    user_name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.UTC))

    def __repr__(self):
        return '<sale id %r product name %r>' % self.id % self.product_name

def get_sales(search):
    search_pattern = f"%{search}"
    results = Sale.query.filter(
        (Sale.id.like(search_pattern)) | (Sale.product_name.like(search_pattern))
        | (Sale.customer_name.like(search_pattern)) | (Sale.customer_email.like(search_pattern))
        | (Sale.user_name.like(search_pattern)) | (Sale.date.like(search_pattern))
    ).all()
    return results