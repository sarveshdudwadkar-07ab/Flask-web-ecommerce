from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

# --- CONFIGURATION ---
app = Flask(__name__)
# CRITICAL: Flask needs a secret key for session management (user login/logout)
app.config['SECRET_KEY'] = 'your_super_secret_key_12345' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CRITICAL FIX FOR LOCALHOST REDIRECT ISSUE
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' 

db = SQLAlchemy(app)

# --- DATABASE MODELS ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_file = db.Column(db.String(50), nullable=False, default='default.jpg')
    cart_items = db.relationship('CartItem', backref='product', lazy=True, cascade="all, delete-orphan")

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

# --- HELPER FUNCTIONS ---

def get_current_user():
    """Retrieves the current logged-in user object."""
    user_id = session.get('user_id') 
    if user_id:
        return User.query.get(user_id)
    return None

def db_init():
    """Initializes the database and adds sample products if none exist."""
    with app.app_context():
        # Create database and tables if they don't exist
        db.create_all() 

        # Add sample products only if the Product table is empty
        if Product.query.count() == 0:
            sample_products = [
                Product(
                    name="Air Jordan 1 Retro", 
                    description="Classic silhouette in a vibrant colorway. Must-have for collectors.", 
                    price=189.99, 
                    image_file="sneaker_1.JPG"
                ),
                Product(
                    name="UltraBoost 21", 
                    description="The ultimate running experience with incredible energy return.", 
                    price=159.00, 
                    image_file="sneaker_2.JPG"
                ),
                Product(
                    name="Nike Air Max 97", 
                    description="Iconic wave design with full-length Max Air cushioning.", 
                    price=175.50, 
                    image_file="sneaker_3.JPG"
                )
            ]
            db.session.add_all(sample_products)
            db.session.commit()
            print("Database initialized with sample products.")
        else:
            print("Database and products already exist.")


# --- ROUTES ---

@app.route('/')
def home():
    """Home page."""
    user = get_current_user()
    if user:
        # If logged in, redirect to the shop dashboard
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if get_current_user():
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            new_user = User(name=name, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Email already registered. Please use a different email or log in.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if get_current_user():
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs the user out."""
    session.pop('user_id', None) 
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    """Main shop dashboard displaying products."""
    user = get_current_user()
    if not user:
        flash('Please log in to view the shop.', 'warning')
        return redirect(url_for('login'))

    products = Product.query.all()
    # Fetch the number of items in the cart to display next to the cart icon
    cart_count = CartItem.query.filter_by(user_id=user.id).count()
    return render_template('dashboard.html', name=user.name, products=products, cart_count=cart_count)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Adds a product to the user's cart."""
    user = get_current_user()
    if not user:
        flash('Please log in to add items to your cart.', 'warning')
        return redirect(url_for('login'))

    product = Product.query.get_or_404(product_id)
    
    cart_item = CartItem.query.filter_by(user_id=user.id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=user.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/cart')
def cart():
    """Displays the shopping cart contents."""
    user = get_current_user()
    if not user:
        flash('Please log in to view your cart.', 'warning')
        return redirect(url_for('login'))

    cart_items = CartItem.query.filter_by(user_id=user.id).all()
    
    cart_with_products = []
    total_price = 0.0

    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product:
            cart_with_products.append((item, product))
            total_price += product.price * item.quantity

    return render_template('cart.html', cart_items=cart_with_products, total_price=total_price)


# --- APPLICATION STARTUP ---
if __name__ == '__main__':
    db_init() # Initialize database and products
    app.run(debug=True)
