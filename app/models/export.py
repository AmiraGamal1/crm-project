from flask import jsonify
from models.sale import Sale
from models.product import Product
from models.customer import Customer


def export_sale_json():
    sales = Sale.query.all()
    sale_list = [{"id": sale.id, "product_name": sale.product_name, "product_quantity": sale.product_quantity,
    "customer_name": sale.customer_name, "customer_email": sale.customer_email,
    "customer_phone": sale.customer_phone, "user_name": sale.user_name,
    "date": sale.date.isoformat()} for sale in sales]

    return sale_list

def export_product_json():
    products = Product.query.all()
    product_list = [{"id": product.id, "product_name": product.product_name,
                      "price": product.price,
                      "product_quantity": product.product_quantity,
                      "date": product.date.isoformat()} for product in products]
    
    return product_list

def export_customer_json():
    customers = Customer.query.all()
    customer_list = [{"id": customer.id, "customer_name": customer.customer_name,
                      "customer_email":customer.customer_email,
                      "customer_phone": customer.customer_phone,
                      "frequentcy_pay": customer.frequentcy_pay,
                      "date": customer.date.isoformat()} for customer in customers]
    
    return customer_list