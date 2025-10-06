# seed.py - creates DB and inserts sample data
from models import db, Product, Location, ProductMovement
from app import app
from datetime import datetime, timedelta
import random

with app.app_context():
    db.drop_all()
    db.create_all()

    # create products
    products = [
        Product(product_id='P-A', name='Product A'),
        Product(product_id='P-B', name='Product B'),
        Product(product_id='P-C', name='Product C'),
        Product(product_id='P-D', name='Product D'),
    ]
    for p in products:
        db.session.add(p)

    # create locations
    locations = [
        Location(location_id='L-1', name='Warehouse X'),
        Location(location_id='L-2', name='Warehouse Y'),
        Location(location_id='L-3', name='Showroom Z'),
    ]
    for l in locations:
        db.session.add(l)

    db.session.commit()

    # create ~20 movements
    now = datetime.utcnow()
    sample_moves = []
    # 10 inbound to locations
    for i in range(8):
        prod = random.choice(products)
        loc = random.choice(locations)
        qty = random.randint(5, 30)
        m = ProductMovement(timestamp=now - timedelta(days=20-i), from_location=None, to_location=loc.location_id, product_id=prod.product_id, qty=qty)
        sample_moves.append(m)
    # 8 transfers between locations
    for i in range(8):
        prod = random.choice(products)
        from_loc = random.choice(locations)
        to_loc = random.choice([l for l in locations if l.location_id != from_loc.location_id])
        qty = random.randint(1, 10)
        m = ProductMovement(timestamp=now - timedelta(days=10-i), from_location=from_loc.location_id, to_location=to_loc.location_id, product_id=prod.product_id, qty=qty)
        sample_moves.append(m)
    # 4 outbound (to None)
    for i in range(4):
        prod = random.choice(products)
        from_loc = random.choice(locations)
        qty = random.randint(1, 8)
        m = ProductMovement(timestamp=now - timedelta(days=5-i), from_location=from_loc.location_id, to_location=None, product_id=prod.product_id, qty=qty)
        sample_moves.append(m)

    for mv in sample_moves:
        db.session.add(mv)
    db.session.commit()
    print("Seeded DB with products, locations and movements.")
