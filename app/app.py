from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, request, redirect
from db import db
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_login import login_required


########### config app #################
app = Flask(__name__)
app.config['SECRET_KEY'] = 'amira' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sales.db'

db.init_app(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

from models.customer import Customer, add_customer, get_customer
from models.product import Product, get_product
from models.sale import Sale, get_sales
from models.user import User, get_user

with app.app_context():
    db.create_all()

        

########### sale routes ###########
# Define routes for sales

@app.route('/view_sale', methods=['GET'])
def view_sale():
    """view Sale table"""
    sales = Sale.query.order_by(Sale.date.desc()).all()
    return render_template('view_sale.html', sales=sales)

@app.route('/search_sale', methods=['GET', 'POST'])
def search_sale():
    search = request.args.get('search', '')
    sales = get_sales(search)
    return render_template('search_sale.html', sales=sales)


@app.route('/add_sale', methods=['POST', 'GET'])
def add_sale():
    """add new sale"""
    if request.method == 'POST':
        product = request.form['product']
        quantity = request.form['quantity']
        customer = request.form['customer']
        customer_email = request.form['customer_email']
        customer_phone = request.form['customer_phone']
        user = request.form['user']
        prod = Product.query.filter_by(product_name=product).first()
        if prod:
            if prod.product_quantity < int(quantity):
                return 'Not enough quantity'
            else:
                prod.product_quantity -= int(quantity)
                try:
                    db.session.commit()
                except:
                    return 'There was an issue updating product quantity'
        else:
            return 'Product not found'
        new_sale = Sale(product_name=product, product_quantity=quantity,
                        customer_name=customer, customer_email=customer_email,
                        customer_phone=customer_phone, user_name=user)
        try:
            db.session.add(new_sale)
            db.session.commit()
            add_customer(new_sale)
            return redirect('/view_sale')
        except:
            return 'There was an issue adding your sale information'
    else:
        return render_template('add_sale.html')
    


    
@app.route('/info_sale/<int:id>', methods=['GET'])
def info_sale(id):
    """view single sale information"""
    sale = Sale.query.get_or_404(id)
    return render_template('info_sale.html', sale=sale)

        
@app.route('/delete_sale/<int:id>')
def delete_sale(id):
    """delete single sale"""
    sale_to_delete = Sale.query.get_or_404(id)

    try:
        db.session.delete(sale_to_delete)
        db.session.commit()
        return redirect('/view_sale')
    except:
        return 'delete error'
    
@app.route('/update_sale/<int:id>', methods=['GET', 'POST'])
def update_sale(id):
    sale = Sale.query.get_or_404(id)
    if request.method == 'POST':
        sale.product_name = request.form['product']
        sale.product_quantity = request.form['quantity']
        sale.customer_name = request.form['customer']
        sale.user_name = request.form['user']

        try:
            db.session.commit()
            return redirect('/view_sale')
        except:
            return 'db update error'
        
    else:
        return render_template('update_sale.html', sale=sale)


########## customer routes ###############
# Define routes for customer

@app.route('/view_customer', methods=['GET'])
def view_customer():
    customers = Customer.query.order_by(Customer.date.desc()).all()
    return render_template('view_customer.html', customers=customers)

@app.route('/search_customer', methods=['GET', 'POST'])
def search_customer():
    search = request.args.get('search', '')
    customers = get_customer(search)
    return render_template('search_customer.html', customers=customers)

########## user route ##################
# Define routes for user

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@app.route('/', methods=['GET', 'POST'])
def  login():
  if request.method == 'POST':
    user_email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(user_email=user_email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return redirect('/view_sale')
  return render_template('login.html')

@app.route('/logout')
@login_required
def  logout():
    logout_user()
    return redirect('/')

@app.route('/view_user', methods=['GET'])
def view_user():
    """view user table"""
    users = User.query.order_by(User.user_name).all()
    return render_template('view_user.html', users=users)

@app.route('/search_user', methods=['GET', 'POST'])
def search_user():
    search = request.args.get('search', '')
    users = get_user(search)
    return render_template('search_user.html', users=users)

@app.route('/add_user', methods=['POST', 'GET'])
def add_user():
    """add user"""
    if request.method == 'POST':
        user_name = request.form['user']
        user_email = request.form['user_email']
        user_phone = request.form['user_phone']
        password = request.form['user_password']
        type = request.form['privilege']
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(user_name=user_name, user_email=user_email,
                        user_phone=user_phone, password=hashed_password,
                        type=type)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/view_user')
        except:
            return 'There was an error adding user'
    else:
        return render_template('add_user.html')
    
@app.route('/info_user/<int:id>', methods=['GET'])
def info_user(id):
    """info single user information"""
    user = User.query.get_or_404(id)
    return render_template('info_user.html', user=user)

@app.route('/delete_user/<int:id>')
def delete_user(id):
    """delete single user"""
    user_to_delete = User.query.get_or_404(id)

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect('/view_user')
    except:
        return 'delete error'
    
@app.route('/update_user/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.user_name = request.form['user']
        user.user_email = request.form['user_email']
        user.user_phone = request.form['user_phone']
        user.password = request.form['user_password']
        user.type = request.form['privilege']

        try:
            db.session.commit()
            return redirect('/view_user')
        except:
            return 'db update error'
        
    else:
        return render_template('update_user.html', user=user)

########## product route ##################
# Define routes for product

@app.route('/view_product', methods=['GET'])
def view_product():
    """view product table"""
    products = Product.query.order_by(Product.product_name).all()
    return render_template('view_product.html', products=products)

@app.route('/search_product', methods=['GET', 'POST'])
def search_product():
    search = request.args.get('search', '')
    products = get_product(search)
    return render_template('search_product.html', products=products)

@app.route('/add_product', methods=['POST', 'GET'])
def add_product():
    """add product"""
    if request.method == 'POST':
        product_name = request.form['product']
        price = request.form['price']
        product_quantity = request.form['quantity']
        existing_product = Product.query.filter_by(product_name=product_name).first()
        if existing_product:
            return "This product is already in the store, try update it!"
        new_product = Product(product_name=product_name, price=price,
                              product_quantity=product_quantity)
        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect('/view_product')
        except:
            return 'There was an error adding your product'
    else:
        return render_template('add_product.html')

@app.route('/info_product/<int:id>', methods=['GET'])
def info_product(id):
    """info single product information"""
    product = Product.query.get_or_404(id)
    return render_template('info_product.html', product=product)

@app.route('/delete_product/<int:id>')
def delete_product(id):
    """delete single sale"""
    product_to_delete = Product.query.get_or_404(id)

    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        return redirect('/view_product')
    except:
        return 'delete error'
    
@app.route('/update_product/<int:id>', methods=['GET', 'POST'])
def update_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.product_name = request.form['product']
        product.price = request.form['price']
        product.product_quantity = request.form['quantity']

        try:
            db.session.commit()
            return redirect('/view_product')
        except:
            return 'db update error'
        
    else:
        return render_template('update_product.html', product=product)


if __name__ == "__main__":
    app.run(debug=True)