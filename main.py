from flask import Flask, request, jsonify, send_file

from quote_manager.database import Base, engine, SessionLocal
from quote_manager.models import Supplier, Product, Quote, QuoteItem, ChecklistItem
from quote_manager.delivery_note import generate_delivery_note

app = Flask(__name__)

# Create tables if not exist
Base.metadata.create_all(bind=engine)


@app.post('/suppliers')
def add_supplier():
    data = request.get_json()
    session = SessionLocal()
    supplier = Supplier(name=data['name'])
    session.add(supplier)
    session.commit()
    return jsonify({'id': supplier.id})


@app.post('/products')
def add_product():
    data = request.get_json()
    session = SessionLocal()
    product = Product(
        supplier_id=data['supplier_id'],
        sku=data['sku'],
        description=data.get('description'),
        price=data.get('price', 0),
        lead_time=data.get('lead_time', 0)
    )
    session.add(product)
    session.commit()
    return jsonify({'id': product.id})


@app.post('/quotes')
def create_quote():
    data = request.get_json()
    session = SessionLocal()
    quote = Quote(
        request_id=data.get('request_id'),
        status=data.get('status', 'draft'),
        value=data.get('value', 0),
        margin=data.get('margin', 0),
        pdf_link=data.get('pdf_link')
    )
    session.add(quote)
    session.flush()
    for item in data.get('items', []):
        qi = QuoteItem(
            quote_id=quote.id,
            product_id=item['product_id'],
            quantity=item.get('quantity', 1)
        )
        session.add(qi)
    session.commit()
    return jsonify({'id': quote.id})


@app.post('/quotes/<int:quote_id>/status')
def update_quote_status(quote_id):
    session = SessionLocal()
    quote = session.get(Quote, quote_id)
    if not quote:
        return {'error': 'not found'}, 404
    data = request.get_json()
    quote.status = data['status']
    session.commit()
    if data['status'] == 'ordered':
        for item in quote.items:
            session.add(ChecklistItem(quote_item_id=item.id))
        session.commit()
    return {'status': quote.status}


@app.get('/quotes/<int:quote_id>/delivery_note')
def get_delivery_note(quote_id):
    item_ids = request.args.getlist('item_id', type=int)
    filename = generate_delivery_note(quote_id, item_ids or None)
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
