from db import db
from datetime import datetime
import pytz



class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    price =  db.Column(db.Integer, nullable=False)
    product_quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.UTC))

    def __repr__(self):
        return '<Product name %r Price %r>' % self.product_name % self.price
    
def get_product(search):
    search_pattern = f"%{search}"
    results = Product.query.filter(
        (Product.id.like(search_pattern)) | (Product.product_name.like(search_pattern))
        | (Product.price.like(search_pattern))
    ).all()
    return results