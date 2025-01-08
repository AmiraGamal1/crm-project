from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, request, redirect, send_file, Response, jsonify, flash, get_flashed_messages
from db import db
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from flask_security import Security, SQLAlchemySessionUserDatastore, roles_accepted
import csv
import io
import json
import os
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, inspect

########### config app #################
app = Flask(__name__)
app.config['SECRET_KEY'] = 'amira'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sales.db'
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

from models.customer import Customer, add_customer, get_customer
from models.product import Product, get_product
from models.sale import Sale, get_sales
from models.user import User, Role, get_user, create_roles
from models.export import export_sale_json, export_product_json, export_customer_json
from models.upload_to_database import allowed_file, parse_products_json_file, parse_products_csv_file, parse_sales_csv_file, parse_sales_json_file

with app.app_context():
    db.create_all()
    create_roles()

datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
security = Security(app, datastore)
########### sale routes ###########
# Define routes for sales

@app.route('/view_sale', methods=['GET'])
@roles_accepted('admin', 'editor', 'supervisor')
def view_sale():
    """view Sale table"""
    sales = Sale.query.order_by(Sale.date.desc()).all()
    return render_template('view_sale.html', sales=sales)

@app.route('/search_sale', methods=['GET', 'POST'])
@roles_accepted('admin', 'editor', 'supervisor')
def search_sale():
    search = request.args.get('search', '')
    sales = get_sales(search)
    return render_template('search_sale.html', sales=sales)


@app.route('/add_sale', methods=['POST', 'GET'])
@roles_accepted('admin', 'editor')
def add_sale():
    """add new sale"""
    if request.method == 'POST':
        error = ""
        product = request.form['product']
        quantity = request.form['quantity']
        customer = request.form['customer']
        customer_email = request.form['customer_email']
        customer_phone = request.form['customer_phone']
        user = request.form['user']
        prod = Product.query.filter_by(product_name=product).first()
        if prod:
            if prod.product_quantity < int(quantity):
                error = 'Not enough quantity'
            else:
                prod.product_quantity -= int(quantity)
                try:
                    db.session.commit()
                except:
                    return 'There was an issue updating product quantity'
        else:
            error = 'Product not found'
        if error:
            return render_template('add_sale.html', product=product,
                                   quantity=quantity, customer=customer,
                                   customer_email=customer_email,
                                   customer_phone=customer_phone,
                                   user=user, error=error)
        new_sale = Sale(product_name=product, product_quantity=quantity,
                        customer_name=customer, customer_email=customer_email,
                        customer_phone=customer_phone, user_name=user)
        try:
            db.session.add(new_sale)
            db.session.commit()
            add_customer(new_sale)
            flash('Successfully added new sale information.', 'success')
        except:
            flash('There was an issue adding your sale information', 'error')
        return redirect('/view_sale')
    else:
        return render_template('add_sale.html')

@app.route('/get_messages')
def get_messages():
    messages = [{'category': category, 'message': message} for category, message in get_flashed_messages(with_categories=True)]
    return jsonify({'messages': messages})


@app.route('/info_sale/<int:id>', methods=['GET'])
@roles_accepted('admin', 'editor', 'supervisor')
def info_sale(id):
    """view single sale information"""
    sale = Sale.query.get_or_404(id)
    return render_template('info_sale.html', sale=sale)


@app.route('/delete_sale/<int:id>')
@roles_accepted('admin', 'editor')
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
@roles_accepted('admin', 'editor')
def update_sale(id):
    sale = Sale.query.get_or_404(id)
    if request.method == 'POST':
        product = request.form['product']
        quantity = request.form['quantity']
        sale.customer_name = request.form['customer']
        sale.user_name = request.form['user']
        prod = Product.query.filter_by(product_name=product).first()
        if prod:
            if prod.product_quantity < int(quantity):
                error = 'Not enough quantity'
            else:
                prod.product_quantity += sale.product_quantity
                prod.product_quantity -= int(quantity)
                sale.product_name = product
                sale.product_quantity = quantity
                try:
                    db.session.commit()
                    return redirect('/view_sale')
                except:
                    return 'db update error'
        else:
            error = 'Product not found'
        return render_template('update_sale.html', sale=sale, error=error)
    else:
        return render_template('update_sale.html', sale=sale)

@app.route('/download_sales')
@roles_accepted('admin')
def download_sales():
    format = request.args.get('format')
    sales_dict = export_sale_json()

    if format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(sales_dict[0].keys())
        for row in sales_dict:
            writer.writerow(row.values())
        output.seek(0)
        response = Response(output, mimetype='test/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=sales.csv'
    elif format == 'json':
        json_data = json.dumps(sales_dict, indent=4)
        response = Response(json_data, mimetype='application/json')
        response.headers['Content-Disposition'] = 'attachment; filename=sales.json'
    else:
        return "Invalid format", 400
    return response

@app.route('/upload_sales', methods=['POST', 'GET'])
@roles_accepted('admin', 'editor')
def upload_sales():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        uploaded_file = request.files['file']
        if uploaded_file == '':
            return jsonify({"error": "No selected file"}), 400

        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            extention = filename.rsplit('.', 1)[1].lower()
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            filename.rsplit('.', 1)[1].lower()
            if extention == 'json':
                msg = parse_sales_json_file(file_path)
                return msg
            elif extention == 'csv':
                inspector = inspect(db.engine)
                return parse_sales_csv_file(inspector, file_path)
            else:
                pass
            return redirect('/view_sale')
        else:
            return jsonify({"error": "File not allowed"}), 400
    return render_template('upload_sales.html')

########## customer routes ###############
# Define routes for customer

@app.route('/view_customer', methods=['GET'])
@roles_accepted('admin', 'editor', 'supervisor')
def view_customer():
    customers = Customer.query.order_by(Customer.date.desc()).all()
    return render_template('view_customer.html', customers=customers)

@app.route('/search_customer', methods=['GET', 'POST'])
@roles_accepted('admin', 'editor', 'supervisor')
def search_customer():
    search = request.args.get('search', '')
    customers = get_customer(search)
    return render_template('search_customer.html', customers=customers)

@app.route('/download_customers')
@roles_accepted('admin')
def download_customers():
    format = request.args.get('format')
    customers_dict = export_customer_json()

    if format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(customers_dict[0].keys())
        for row in customers_dict:
            writer.writerow(row.values())
        output.seek(0)
        response = Response(output, mimetype='test/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=customers.csv'
    elif format == 'json':
        json_data = json.dumps(customers_dict, indent=4)
        response = Response(json_data, mimetype='application/json')
        response.headers['Content-Disposition'] = 'attachment; filename=customers.json'
    else:
        return jsonify("Invalid format"), 400
    return response

########## user route ##################
# Define routes for user


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@app.route('/', methods=['GET', 'POST'])
def  login():
  error = ""
  if request.method == 'POST':
    user_email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(user_email=user_email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return redirect('/view_sale')
    else:
        error = "incorrect password"
  return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def  logout():
    logout_user()
    return redirect('/')

@app.route('/view_user', methods=['GET'])
@roles_accepted('admin', 'supervisor')
def view_user():
    """view user table"""
    users = User.query.order_by(User.user_name).all()
    return render_template('view_user.html', users=users)

@app.route('/search_user', methods=['GET', 'POST'])
@roles_accepted('admin','supervisor')
def search_user():
    search = request.args.get('search', '')
    users = get_user(search)
    return render_template('search_user.html', users=users)

@app.route('/add_user', methods=['POST', 'GET'])
@roles_accepted('admin')
def add_user():
    """add user"""
    if request.method == 'POST':
        user_name = request.form['user']
        user_email = request.form['user_email']
        user_phone = request.form['user_phone']
        password = request.form['user_password']
        user_role = request.form['privilege']

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        role = Role.query.filter_by(name=user_role).first()
        new_user = User(user_name=user_name, user_email=user_email,
                        user_phone=user_phone, password=hashed_password)
        new_user.roles.append(role)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/view_user')
        except:
            return 'There was an error adding user'
    else:
        return render_template('add_user.html')

@app.route('/info_user/<int:id>', methods=['GET'])
@roles_accepted('admin', 'supervisor')
def info_user(id):
    """info single user information"""
    user = User.query.get_or_404(id)
    return render_template('info_user.html', user=user)

@app.route('/delete_user/<int:id>')
@roles_accepted('admin')
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
@roles_accepted('admin')
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
@roles_accepted('admin', 'editor', 'supervisor')
def view_product():
    """view product table"""
    products = Product.query.order_by(Product.product_name).all()
    return render_template('view_product.html', products=products)

@app.route('/search_product', methods=['GET', 'POST'])
@roles_accepted('admin', 'editor', 'supervisor')
def search_product():
    search = request.args.get('search', '')
    products = get_product(search)
    return render_template('search_product.html', products=products)

@app.route('/add_product', methods=['POST', 'GET'])
@roles_accepted('admin', 'editor')
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
@roles_accepted('admin', 'editor', 'supervisor')
def info_product(id):
    """info single product information"""
    product = Product.query.get_or_404(id)
    return render_template('info_product.html', product=product)

@app.route('/delete_product/<int:id>')
@roles_accepted('admin', 'editor')
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
@roles_accepted('admin', 'editor')
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

@app.route('/download_products')
@roles_accepted('admin', 'editor')
def download_products():
    format = request.args.get('format')
    products_dict = export_product_json()

    if format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(products_dict[0].keys())
        for row in products_dict:
            writer.writerow(row.values())
        output.seek(0)
        response = Response(output, mimetype='test/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=products.csv'
    elif format == 'json':
        json_data = json.dumps(products_dict, indent=4)
        response = Response(json_data, mimetype='application/json')
        response.headers['Content-Disposition'] = 'attachment; filename=products.json'
    else:
        return "Invalid format", 400
    return response

@app.route('/upload_products', methods=['POST', 'GET'])
@roles_accepted('admin', 'editor')
def upload_products():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        uploaded_file = request.files['file']
        if uploaded_file == '':
            return jsonify({"error": "No selected file"}), 400

        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            extention = filename.rsplit('.', 1)[1].lower()
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            filename.rsplit('.', 1)[1].lower()
            if extention == 'json':
                msg = parse_products_json_file(file_path)
                return msg
            elif extention == 'csv':
                inspector = inspect(db.engine)
                msg = parse_products_csv_file(inspector, file_path)
                return msg
            else:
                pass
            return redirect('/view_product')
        else:
            return jsonify({"error": "File not allowed"}), 400
    return render_template('upload_products')


if __name__ == "__main__":
    app.run(debug=True)
