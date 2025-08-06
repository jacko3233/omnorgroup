from fpdf import FPDF
from .database import SessionLocal
from .models import Quote


def generate_delivery_note(quote_id, item_ids=None, filename='delivery_note.pdf'):
    session = SessionLocal()
    quote = session.get(Quote, quote_id)
    if not quote:
        session.close()
        raise ValueError('Quote not found')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)
    pdf.cell(0, 10, f'Delivery Note for Quote {quote.id}', ln=1)
    pdf.cell(0, 10, f'Status: {quote.status}', ln=1)
    pdf.ln(5)
    items = quote.items
    if item_ids:
        items = [it for it in items if it.id in item_ids]
    for item in items:
        prod = item.product
        pdf.cell(0, 10, f'{prod.sku} - {prod.description} x {item.quantity}', ln=1)
    pdf.output(filename)
    session.close()
    return filename
