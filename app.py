from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, Product, Location, ProductMovement
from forms import ProductForm, LocationForm, MovementForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'  # change for production
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ---- Flask 3.x fix: before_first_request is removed ----
# We'll create tables when the app starts, inside app context
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

# --- Products CRUD ---
@app.route('/products')
def products():
    items = Product.query.all()
    return render_template('products.html', products=items)

@app.route('/product/add', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        p = Product(product_id=form.product_id.data.strip(), name=form.name.data.strip())
        db.session.add(p)
        db.session.commit()
        flash('Product added.')
        return redirect(url_for('products'))
    return render_template('product_form.html', form=form, action='Add')

@app.route('/product/edit/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    p = Product.query.get_or_404(product_id)
    form = ProductForm(obj=p)
    if form.validate_on_submit():
        p.name = form.name.data.strip()
        db.session.commit()
        flash('Product updated.')
        return redirect(url_for('products'))
    return render_template('product_form.html', form=form, action='Edit')

@app.route('/product/delete/<product_id>', methods=['POST'])
def delete_product(product_id):
    p = Product.query.get_or_404(product_id)
    db.session.delete(p)
    db.session.commit()
    flash('Product deleted.')
    return redirect(url_for('products'))

# --- Locations CRUD ---
@app.route('/locations')
def locations():
    items = Location.query.all()
    return render_template('locations.html', locations=items)

@app.route('/location/add', methods=['GET', 'POST'])
def add_location():
    form = LocationForm()
    if form.validate_on_submit():
        l = Location(location_id=form.location_id.data.strip(), name=form.name.data.strip())
        db.session.add(l)
        db.session.commit()
        flash('Location added.')
        return redirect(url_for('locations'))
    return render_template('location_form.html', form=form, action='Add')

@app.route('/location/edit/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    l = Location.query.get_or_404(location_id)
    form = LocationForm(obj=l)
    if form.validate_on_submit():
        l.name = form.name.data.strip()
        db.session.commit()
        flash('Location updated.')
        return redirect(url_for('locations'))
    return render_template('location_form.html', form=form, action='Edit')

@app.route('/location/delete/<location_id>', methods=['POST'])
def delete_location(location_id):
    l = Location.query.get_or_404(location_id)
    db.session.delete(l)
    db.session.commit()
    flash('Location deleted.')
    return redirect(url_for('locations'))

# --- Movements CRUD ---
@app.route('/movements')
def movements():
    moves = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    return render_template('movements.html', movements=moves)

def _choices_for_movement():
    products = [(p.product_id, f"{p.product_id} - {p.name}") for p in Product.query.order_by(Product.name).all()]
    locations = [('', '---')] + [(l.location_id, f"{l.location_id} - {l.name}") for l in Location.query.order_by(Location.name).all()]
    return products, locations

@app.route('/movement/add', methods=['GET', 'POST'])
def add_movement():
    form = MovementForm()
    products, locations = _choices_for_movement()
    form.product_id.choices = products
    form.from_location.choices = locations
    form.to_location.choices = locations
    if form.validate_on_submit():
        from_loc = form.from_location.data or None
        to_loc = form.to_location.data or None
        mv = ProductMovement(product_id=form.product_id.data, from_location=from_loc, to_location=to_loc, qty=form.qty.data)
        db.session.add(mv)
        db.session.commit()
        flash('Movement recorded.')
        return redirect(url_for('movements'))
    return render_template('movement_form.html', form=form, action='Add')

@app.route('/movement/delete/<int:movement_id>', methods=['POST'])
def delete_movement(movement_id):
    mv = ProductMovement.query.get_or_404(movement_id)
    db.session.delete(mv)
    db.session.commit()
    flash('Movement deleted.')
    return redirect(url_for('movements'))

# --- Report: balance per product per location ---
@app.route('/report')
def report():
    from sqlalchemy import func

    products = Product.query.order_by(Product.name).all()
    locations = Location.query.order_by(Location.name).all()

    balances = []
    for p in products:
        for loc in locations:
            incoming = db.session.query(func.coalesce(func.sum(ProductMovement.qty), 0)).filter(
                ProductMovement.product_id == p.product_id,
                ProductMovement.to_location == loc.location_id
            ).scalar()

            outgoing = db.session.query(func.coalesce(func.sum(ProductMovement.qty), 0)).filter(
                ProductMovement.product_id == p.product_id,
                ProductMovement.from_location == loc.location_id
            ).scalar()

            qty = incoming - outgoing
            balances.append({'product': p, 'location': loc, 'qty': qty})

    return render_template('report.html', balances=balances)

if __name__ == '__main__':
    app.run(debug=True)
