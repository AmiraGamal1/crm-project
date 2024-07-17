from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sales.db'
db = SQLAlchemy(app)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    product_quantity = db.Column(db.Integer, nullable=False)
    customer_name = db.Column(db.String(200), nullable=False)
    user_name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.UTC))

    def __repr__(self):
        return '<product name %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        product = request.form['product']
        quantity = request.form['quantity']
        customer = request.form['customer']
        user = request.form['user']
        new_sale = Sale(product_name=product, product_quantity=quantity,
                        customer_name=customer, user_name=user)
        try:
            db.session.add(new_sale)
            db.session.commit()
            return redirect('/')
        except:
            return 'db error'
    else:
        sales = Sale.query.order_by(Sale.date).all()
        return render_template('index.html', sales=sales)
    
@app.route('/delete/<int:id>')
def delete(id):
    sale_to_delete = Sale.query.get_or_404(id)

    try:
        db.session.delete(sale_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'delete error'
    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    sale = Sale.query.get_or_404(id)
    if request.method == 'POST':
        sale.product_name = request.form['product']
        sale.product_quantity = request.form['quantity']
        sale.customer_name = request.form['customer']
        sale.user_name = request.form['user']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'db update error'
        
    else:
        return render_template('update.html', sale=sale)
    

if __name__ == "__main__":
    app.run(debug=True)
