from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    wishlist = db.relationship('Wishlist', backref='user', lazy=True)




class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    writer = db.Column(db.String(100), nullable=False)
    cover_image = db.Column(db.String(100), nullable=True)
    pdf_file = db.Column(db.String(100), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)  # Foreign key reference
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Book {self.title}>'


class BookType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', backref='book_type', lazy=True)
    weekly_activities = db.relationship('WeeklyActivity', backref='book_type', lazy=True)
    daily_activities = db.relationship('DailyActivity', backref='book_type', lazy=True)

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)

class WeeklyActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    book_type_id = db.Column(db.Integer, db.ForeignKey('book_type.id'), nullable=False)
    week_start_date = db.Column(db.Date, nullable=False)
    total_views = db.Column(db.Integer, default=0)
    total_downloads = db.Column(db.Integer, default=0)

class DailyActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    book_type_id = db.Column(db.Integer, db.ForeignKey('book_type.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_views = db.Column(db.Integer, default=0)
    total_downloads = db.Column(db.Integer, default=0)
