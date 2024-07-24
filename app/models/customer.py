from db import db
from datetime import datetime
import pytz

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(15))
    frequentcy_pay = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.UTC))

    def __repr__(self):
        return '<Customer name %r Email %r>' % self.customer_name % self.customer_email
    
def add_customer(sale):
    existing_customer = Customer.query.filter_by(customer_email=sale.customer_email).first()
    if existing_customer:
        existing_customer.frequentcy_pay += 1
    else:
        new_customer = Customer(customer_name=sale.customer_name,
                                customer_email=sale.customer_email,
                                customer_phone=sale.customer_phone,
                                frequentcy_pay=1)    
        db.session.add(new_customer)
    try:
        db.session.commit()
    except:
        return 'There was an issue adding new customer'
    return 'Customer added/updated successfully'

def get_customer(search):
    search_pattern = f"%{search}"
    results = Customer.query.filter(
        (Customer.id.like(search_pattern)) | (Customer.customer_name.like(search_pattern))
        | (Customer.customer_email.like(search_pattern)) | (Customer.customer_phone.like(search_pattern))
        | (Customer.date.like(search_pattern))
    ).all()
    return results