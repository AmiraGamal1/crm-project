import json
from flask import jsonify
from models.sale import Sale
from db import db
from models.product import Product
from models.customer import add_customer
import pandas as pd
import numpy as np



ALLOWED_EXTENSIONS = {'csv', 'json'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_sales_json_file(data):
    for item in data:
        if 'product_name'  not in item or \
            'product_quantity' not in item or 'customer_name' not in item or \
                'customer_email' not in item or 'customer_phone' not in item \
                or 'user_name' not in item:
            return False
        if  not isinstance(item['product_name' ], str) or \
             not isinstance(item['product_quantity'], int) or \
                not isinstance(item['customer_name'], str) or \
                not isinstance(item['customer_email'], str) or \
                    not isinstance(item['customer_phone'], str) or\
                not isinstance(item['user_name'], str):
            return False
    return True
        
def handle_json_file(file_path):
    with open(file_path) as file:
        data = json.load(file)
    if not validate_sales_json_file(data):
        return jsonify({"error": "Invalid data"})
    
    for item in data:
        prod = Product.query.filter_by(product_name=item['product_name']).first()
        if prod:
            if prod.product_quantity < int(item['product_quantity']):
                return jsonify({"error":'Not enough quantity'})
            else:
                prod.product_quantity -= int(item['product_quantity'])
                try:
                    db.session.commit()
                except:
                    return jsonify({"error":'There was an issue updating product quantity'})
        else:
            return jsonify({"error":'Product not found'})
        
        sale = Sale(product_name=item['product_name'], product_quantity=item['product_quantity'],
                        customer_name=item['customer_name'], customer_email=item['customer_email'],
                        customer_phone=item['customer_phone'], user_name=item['user_name'])
        db.session.add(sale)
        db.session.commit()
        add_customer(sale)
    return jsonify({"message": "Sales added successfully"})

def validate_sales_csv_file(inspector ,table, csvData):
    columns = inspector.get_columns(table)
    db_columns = {col['name']: str(col['type'])  for col in columns if col['name'] != 'id' and col['name'] != 'date'}
    missing_columns = [col for col in db_columns if col not in csvData.columns]
    if missing_columns:
        return False, jsonify({"missing columns": missing_columns})
    if not isinstance(csvData['product_quantity'].iloc[0], np.int64):
        return False, jsonify({"incorrect data type": f"data type of {'product_quantity'} is {db_columns['product_quantity'].python_type.__name__} put fount {type(csvData['product_quantity'].iloc[0]).__name__}"})
    return True, jsonify("successfly add objects")



def parseCSV(inspector, file_path):
    csvData = pd.read_csv(file_path)
    stat, mesg = validate_sales_csv_file(inspector,'sales', csvData)
    if not stat:
        return mesg
    for i, row in csvData.iterrows():
        prod = Product.query.filter_by(product_name=row['product_name']).first()
        if prod:
            if prod.product_quantity < int(row['product_quantity']):
                return jsonify({"error":'Not enough quantity'})
            else:
                prod.product_quantity -= int(row['product_quantity'])
                try:
                    db.session.commit()
                except:
                    return jsonify({"error":'There was an issue updating product quantity'})
        else:
            return jsonify({"error":'Product not found'})
        sale = Sale(product_name=row['product_name'], product_quantity=row['product_quantity'],
                        customer_name=row['customer_name'], customer_email=row['customer_email'],
                        customer_phone=row['customer_phone'], user_name=row['user_name'])
        try:
            db.session.add(sale)
            db.session.commit()
            add_customer(sale)
        except:
            return jsonify({"error": "database error"})
    return jsonify({"message": "Sales added successfully"})