from app import app
from app.models.product import Product
from flask import render_template, redirect, url_for, request, send_from_directory
from os import listdir, path
import json

@app.route('/')
@app.route('/index')
def index():
    return render_template('layout.html.jinja')

@app.route('/extract', methods=['GET', 'POST'])
def extract():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        product = Product(product_id)
        product.extract_product()
        product.save_to_json()
        return redirect(url_for('opinions', product_id = product_id))
    return render_template('extract.html.jinja')

@app.route('/products')
def products():
    data_list = []
    products_list = [product.split('.')[0] for product in listdir("app/products")]
    for product in products_list:
        with open(f'app/products/{product}.json', 'r') as opinions:
            json_arr = json.load(opinions)
            data_list.append({'id':json_arr['product_id'], 'name':json_arr['product_name'], 'number_of_opinions':str(json_arr['number_of_opinions']), 'pros_count':str(json_arr['pros_count']), 'cons_count':str(json_arr['cons_count']), 'score':str(json_arr['score'])})
    
    return render_template('products.html.jinja', products=data_list)

@app.route('/opinions/<product_id>')
def opinions(product_id):
    product = Product(product_id)
    product.read_from_json()
    return render_template('opinions.html.jinja', product=str(product))

@app.route('/charts/<product_id>')
def charts(product_id):
    pass

@app.route('/about')
def about():
    return render_template('about.html.jinja')

@app.route('/download/<product_id>')
def download(product_id):
    return send_from_directory(directory = 'products', path = f'{product_id}.json', as_attachment = True)
