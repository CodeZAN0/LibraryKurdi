
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory,jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user
from datetime import datetime, timedelta , timezone
from forms import LoginForm, RegisterForm, BookForm  # Import your forms
from models import Category, Book  # Import your models
from sqlalchemy import Column, Integer, String, ForeignKey,create_engine
from sqlalchemy.orm import relationship,sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from sqlalchemy import Column, Integer, String


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dhbvwirfb379@'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Create the directories if they do not exist
os.makedirs('static/covers', exist_ok=True)
os.makedirs('static/pdfs', exist_ok=True)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    writer = db.Column(db.String(100), nullable=False)
    cover_image = db.Column(db.String(200), nullable=False)
    pdf_file = db.Column(db.String(200), nullable=False)
    activities = db.relationship('UserActivity', back_populates='book')
    wishlists = db.relationship('Wishlist', back_populates='book')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)  # Foreign key for Category
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'writer': self.writer,
            'cover_image': self.cover_image,
            'pdf_file': self.pdf_file,
            'category': self.category.name if self.category else None
        }


class User(db.Model):
    __tablename__ = 'user' 
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100))
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    password_hash = Column(String(128))
    avatar = Column(String(100))  # Ensure this line exists
    phone = Column(String(15))
    location = Column(String(100))
    account_created = db.Column(db.DateTime, default=datetime.utcnow)
    activities = db.relationship('UserActivity', back_populates='user', cascade="all, delete-orphan")
    wishlists = db.relationship('Wishlist', back_populates='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
class Writer(db.Model):
    __tablename__ = 'writers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    num_books = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=False)  # Store the filename of the image

    def __repr__(self):
        return f"<Writer {self.name}>"

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    activity_type = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='activities')
    book = db.relationship('Book', back_populates='activities')

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

    user = db.relationship('User', back_populates='wishlists')
    book = db.relationship('Book', back_populates='wishlists')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    icon = db.Column(db.String(10), nullable=False)
    books = db.relationship('Book', backref='category', lazy=True)  # Relationship to Book

# Form for adding/editing categories
class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    icon = StringField('Icon', validators=[DataRequired()])
    submit = SubmitField('Submit')
@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

@app.route('/category')
def category():
    categories = Category.query.all()
    return render_template('category.html',  categories=categories)
@app.route('/categories')
def categories():
    categories = Category.query.all()  # Fetch all categories from the database
    return render_template('categories.html', categories=categories)


@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        new_category = Category(
            name=form.name.data,
            description=form.description.data,
            icon=form.icon.data
        )
        db.session.add(new_category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
    return render_template('add_category.html', form=form)  # Render the form again if there's an error


# Route to edit a category
@app.route('/edit_category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.icon = form.icon.data
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_category.html', form=form, category=category)

# Route to delete a category
@app.route('/delete_category/<int:id>')
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/categories', methods=['GET', 'POST'])
def admin_categories():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, description=form.description.data, icon=form.icon.data)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('admin_categories'))  # After adding, redirect back to the category admin page
    categories = Category.query.all()  # Fetch all categories to display
    return render_template('admin_categories.html', form=form, categories=categories)

@app.route('/category/<int:category_id>')
def category_books(category_id):
    # Fetch books by category ID from the database
    books = Book.query.filter_by(category_id=category_id).all()
    return render_template('category_books.html', books=books)

@app.route('/category/<int:category_id>')
def books_by_category(category_id):
    category = Category.query.get_or_404(category_id)  # Get the category or show 404 if not found
    books = Book.query.filter_by(category_id=category_id).all()  # Get books for this category
    return render_template('books_by_category.html', category=category, books=books)

@app.route('/wishlist')
def wishlist():
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash('You need to log in to view your wishlist.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    wishlists = Wishlist.query.filter_by(user_id=user.id).all()
    books = [Book.query.get(wishlist.book_id) for wishlist in wishlists]
    return render_template('wishlist.html', books=books)



@app.route('/add_to_wishlist/<int:book_id>', methods=['POST'])
def add_to_wishlist(book_id):
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash('You need to be logged in to add to wishlist.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Check if the book is already in the user's wishlist
    existing_wishlist = Wishlist.query.filter_by(user_id=user_id, book_id=book_id).first()
    if existing_wishlist:
        flash('Book already in wishlist.', 'info')
    else:
        # Add to wishlist
        new_wishlist = Wishlist(user_id=user_id, book_id=book_id)
        db.session.add(new_wishlist)
        db.session.commit()

        # Log the activity
        new_activity = UserActivity(user_id=user_id, book_id=book_id, activity_type='wishlist')
        db.session.add(new_activity)
        db.session.commit()
        
        flash('Book added to wishlist!', 'success')
    
    return redirect(url_for('index'))




@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    # Ensure admin is logged in
    if 'user_id' not in session or not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    form = CategoryForm()

    # Handle book addition via form submission
    if request.method == 'POST' and 'add_book' in request.form:
        title = request.form['title'].strip()  # Strip whitespace
        description = request.form['description'].strip()
        writer = request.form['writer'].strip()
        category_id = request.form['category']  # Get selected category ID

        # Handle file uploads
        cover_image = request.files['cover']
        pdf_file = request.files['file']

        # Validate form fields
        if not title or not description or not writer or not category_id:
            flash('Title, description, writer, and category fields cannot be empty.', 'danger')
            return redirect(url_for('admin_dashboard'))

        # Validate file types (example for image and pdf)
        if not cover_image or not cover_image.filename.endswith(('.png', '.jpg', '.jpeg')):
            flash('Cover image must be a PNG or JPEG file.', 'danger')
            return redirect(url_for('admin_dashboard'))

        if not pdf_file or not pdf_file.filename.endswith('.pdf'):
            flash('PDF file must be a PDF document.', 'danger')
            return redirect(url_for('admin_dashboard'))

        # Use secure_filename to prevent directory traversal attacks
        cover_image_filename = secure_filename(cover_image.filename)
        pdf_file_filename = secure_filename(pdf_file.filename)

        cover_image_path = os.path.join('static/covers', cover_image_filename)
        pdf_file_path = os.path.join('static/pdfs', pdf_file_filename)

        # Save files to the designated paths
        cover_image.save(cover_image_path)
        pdf_file.save(pdf_file_path)


        # Create new book entry
        book = Book(
            title=title,
            description=description,
            writer=writer,
            cover_image=cover_image_filename,
            pdf_file=pdf_file_filename,
            category_id=category_id  # Set the selected category ID
        )

        try:
            db.session.add(book)
            db.session.commit()
            flash('Book added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error adding book: {}'.format(str(e)), 'danger')

        return redirect(url_for('admin_dashboard'))

    # Render data for the dashboard
    books = Book.query.all()
    writers = Writer.query.all()
    categories = Category.query.all()

    # Render admin dashboard template
    return render_template('admin_dashboard.html', 
                           books=books, 
                           writers=writers,
                           categories=categories,
                           form=form)







@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Query the admin user from the database
        admin = Admin.query.filter_by(email=email).first()

        if admin and check_password_hash(admin.password, password):
            # Set the session variables
            session['admin_logged_in'] = True
            session['admin_id'] = admin.id
            
            # Redirect to the admin dashboard
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('admin_login.html')


@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        email = request.form.get('email')  # Safely retrieve form data
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required!', 'danger')
            return redirect(url_for('admin_register'))
        
        # Rest of the registration logic
        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            flash('Admin with this email already exists.', 'danger')
            return redirect(url_for('admin_register'))
        
        new_admin = Admin(email=email)
        new_admin.set_password(password)
        
        db.session.add(new_admin)
        db.session.commit()
        
        flash('Admin registered successfully!', 'success')
        return redirect(url_for('admin_login'))
    
    return render_template('admin_register.html')

@app.route('/admin_logout')
def admin_logout():
    # Clear the admin session
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    
    # Flash a message (optional)
    flash('You have been logged out.', 'info')
    
    # Redirect to the admin login page
    return redirect(url_for('admin_login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.identifier.data
        password = form.password.data

        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('login.html', form=form)


@app.route('/some_route')
def some_route():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)  # Updated line
        if user:
            # Do something with the user
            return f"Hello, {user.username}!"
        else:
            flash('User not found', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Please log in first', 'warning')
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()  # Instantiate the registration form
    if form.validate_on_submit():  # Check if the form is submitted and valid
        full_name = form.full_name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        avatar = form.avatar.data
        location = form.location.data  # Get the location
        phone = form.phone.data  # Get the phone number

        # Check if the user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        # Create the new user
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            location=location,
            phone=phone  # Make sure to add a comma after this if more attributes follow
        )
        new_user.set_password(password)  # Hash the password

        # Handle avatar file upload if needed
        if avatar and allowed_file(avatar.filename):
            filename = secure_filename(avatar.filename)
            avatar_path = os.path.join('static/avatars', filename)  # Ensure the directory is correct
            avatar.save(avatar_path)  # Save the avatar file
            new_user.avatar = filename  # Save the filename to the user object

        # Add the new user to the session and commit
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)





@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user)
@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        # Process form data and update user
        user.full_name = request.form['full_name']
        user.email = request.form['email']
        # Add other fields as necessary

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile', user_id=user.id))

    return render_template('edit_profile.html', user=user)
@app.context_processor
def inject_user():
    user = None  # Default value
    # Here you should implement your logic to get the logged-in user
    if 'user_id' in session:  # Assuming you're storing user_id in session after login
        user = User.query.get(session['user_id'])
    return {'user': user}
    

def save_file(file, folder):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(folder, filename))
        return filename
    return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'pdf']



@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    form = BookForm()

    # Fetch all categories to populate the select field
    form.category.choices = [(category.id, category.name) for category in Category.query.all()]


    if form.validate_on_submit():
        cover_filename = save_file(form.cover.data, 'static/covers')
        pdf_filename = save_file(form.file.data, 'static/pdfs')
        
        new_book = Book(
            title=form.title.data,
            description=form.description.data,
            writer=form.writer.data,
            cover_image=cover_filename,
            pdf_file=pdf_filename,
            category_id=form.category.data
        )
        
        db.session.add(new_book)
        db.session.commit()

        flash('Book added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_book.html', form=form)

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        book.title = request.form['title']
        book.description = request.form['description']
        book.writer = request.form['writer']
        
        # Handle cover image upload
        if 'cover' in request.files:
            cover = request.files['cover']
            if cover and allowed_file(cover.filename):
                cover_filename = secure_filename(cover.filename)
                cover.save(os.path.join('static/covers', cover_filename))
                book.cover_image = cover_filename

        # Handle PDF file upload
        if 'file' in request.files:
            pdf_file = request.files['file']
            if pdf_file and allowed_file(pdf_file.filename):
                file_filename = secure_filename(pdf_file.filename)
                pdf_file.save(os.path.join('static/pdfs', file_filename))
                book.pdf_file = file_filename

        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books_list'))

    return render_template('edit_book.html', book=book)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'pdf']

@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
            flash('Book successfully deleted!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error occurred: {str(e)}', 'danger')
    else:
        flash('Book not found.', 'warning')

    return redirect(url_for('books_list'))
   
@app.route('/download/<filename>')
def download_file(filename):
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash('You need to be logged in to download the book.', 'warning')
        return redirect(url_for('login'))

    # Ensure the file exists and is linked to a book in the database
    book = Book.query.filter_by(pdf_file=filename).first_or_404()

    # Record the download activity in the UserActivity model
    activity = UserActivity(
        user_id=session['user_id'],
        book_id=book.id,
        activity_type='download'
    )
    db.session.add(activity)
    db.session.commit()

    # Serve the PDF file for download securely
    return send_from_directory('static/pdfs', filename, as_attachment=True)




@app.route('/read/<filename>')
def read_online(filename):
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash('You need to be logged in to read the book.', 'warning')
        return redirect(url_for('login'))
    
    book = Book.query.filter_by(pdf_file=filename).first_or_404()
    
    # Record the activity
    activity = UserActivity(
        user_id=session['user_id'],
        book_id=book.id,
        activity_type='read'
    )
    db.session.add(activity)
    db.session.commit()
    
    return render_template('read_online.html', book=book)


@app.route('/delete_activity/<int:activity_id>', methods=['POST'])
def delete_activity(activity_id):
    # Find the activity by ID
    activity = Activity.query.get(activity_id)
    
    if activity:
        try:
            # Delete the activity
            db.session.delete(activity)
            db.session.commit()
            flash('Activity successfully deleted!', 'success')
        except Exception as e:
            # Rollback in case of error
            db.session.rollback()
            flash(f'Error occurred: {str(e)}', 'danger')
    else:
        flash('Activity not found.', 'warning')

    # Redirect back to the admin dashboard or any other page
    return redirect(url_for('admin_dashboard'))

@app.route('/view_activity/<int:id>')
def view_activity(id):
    activity = get_activity_by_id(id)  # Replace with your actual function to get the activity
    if activity is None:
        abort(404)  # or handle the error as needed
    return render_template('view_activity.html', activity=activity)


@app.route('/book/<int:id>')
def book_detail(id):
    book = Book.query.get_or_404(id)
    return render_template('book_detail.html', book=book)

@app.route('/books_list')
def books_list():
    books = Book.query.all()  # Retrieves all books from the database
    return render_template('books_list.html', books=books)

# Example function to fetch user activities
def get_user_activities():
    # Replace with your logic to fetch activities, e.g., from a database
    return [
        {'activity': 'Logged in', 'timestamp': '2024-09-14 10:00'},
        {'activity': 'Downloaded a book', 'timestamp': '2024-09-14 10:15'}
    ]


@app.route('/user_activities')
def user_activities():
    books = Book.query.all()  # Retrieves all books from the database
    # Fetch user activities
    activities = get_user_activities()  # Replace this with your actual function
    return render_template('user_activities.html', activities=activities )

# Function to fetch top 10 downloaded books
def get_top_downloaded_books():
    try:
        # Fetch top 10 downloaded books from the database
        return db.session.query(Book).order_by(Book.download_count.desc()).limit(10).all()
    except Exception as e:
        print(f"Error fetching top downloaded books: {e}")
        return []

@app.route('/top_downloaded_books')
def top_downloaded_books():
    top_downloaded_books = get_top_downloaded_books()
    return render_template('top_downloaded_books.html', top_downloaded_books=top_downloaded_books)


@app.route('/top_read_books')
def top_read_books():
    # Fetch top read books
    top_read_books = get_top_read_books()  # Replace with actual function
    return render_template('top_read_books.html', top_read_books=top_read_books)


@app.route('/book/<int:book_id>')
def book_details(book_id):
    # Sample book data. In a real application, this would come from a database.
    books = {
        1: {
            'title': 'Sample Book Title',
            'author': 'Author Name',
            'description': 'This is a brief description of the book.',
            'summary': 'This section provides a detailed summary of the book.'
        },
        # Add more books as needed
    }

    book = books.get(book_id)
    if not book:
        return "Book not found!", 404

    return render_template('book_details.html', book=book)



@app.route('/writers')
def writers_page():
    writers = Writer.query.all()  # Fetch all writers from the database
    return render_template('writers.html', writers=writers)

# Route to add a new writer
@app.route('/admin/add_writer', methods=['POST'])
def add_writer():
    name = request.form['name']
    bio = request.form['bio']
    num_books = request.form['num_books']
    image = request.files['image']

    # Save image to static/images directory
    filename = secure_filename(image.filename)
    image.save(os.path.join('static/writers', filename))

    new_writer = Writer(name=name, bio=bio, num_books=num_books, image=filename)
    db.session.add(new_writer)
    db.session.commit()

    flash("Writer added successfully!", "success")
    return redirect(url_for('admin_dashboard'))

# Route to delete a writer
@app.route('/admin/delete_writer/<int:writer_id>', methods=['POST'])
def delete_writer(writer_id):
    writer = Writer.query.get_or_404(writer_id)
    db.session.delete(writer)
    db.session.commit()

    flash("Writer deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_writer/<int:writer_id>', methods=['GET', 'POST'])
def edit_writer(writer_id):
    writer = Writer.query.get_or_404(writer_id)
    
    if request.method == 'POST':
        writer.name = request.form['name']
        writer.bio = request.form['bio']
        writer.num_books = request.form['num_books']
        
        if 'image' in request.files:
            image = request.files['image']
            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join('static/writers', filename))
                writer.image = filename

        db.session.commit()
        flash("Writer updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_writer.html', writer=writer)

# Route to get all books
@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books])

# Route to get a specific book by ID
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if book:
        return jsonify(book.to_dict())
    else:
        return jsonify({"error": "Book not found"}), 404
# Route to update a book's availability
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get(book_id)
    if book:
        data = request.get_json()
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.available = data.get('available', book.available)
        db.session.commit()
        return jsonify(book.to_dict())
    else:
        return jsonify({"error": "Book not found"}), 404

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
