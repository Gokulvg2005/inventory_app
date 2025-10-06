# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    product_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<Product {self.product_id} {self.name}>"

class Location(db.Model):
    location_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<Location {self.location_id} {self.name}>"

class ProductMovement(db.Model):
    movement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    from_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    product_id = db.Column(db.String(50), db.ForeignKey('product.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    # relationships for convenience
    product = db.relationship('Product', backref='movements')
    from_loc = db.relationship('Location', foreign_keys=[from_location], backref='out_movements')
    to_loc = db.relationship('Location', foreign_keys=[to_location], backref='in_movements')

    def __repr__(self):
        return f"<Movement {self.movement_id} {self.product_id} {self.qty}>"
