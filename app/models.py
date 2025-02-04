from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

import re
from app import db, bcrypt



class Membership(db.Model):
    __tablename__ = 'memberships'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    features = db.Column(db.Text, nullable=True)

    users = db.relationship("User", back_populates="membership")
    


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)  
    membership_id = db.Column(db.Integer, db.ForeignKey("memberships.id"), nullable=True)  
    membership = db.relationship("Membership", back_populates="users")
    # Relationship: One user can have many bookings
    bookings = db.relationship("Booking", backref="user", lazy=True, cascade="all, delete-orphan")
    membership = db.relationship("Membership", back_populates="users")
    @validates("email")
    def validate_email(self, key, email):
        """Ensure email is unique and formatted correctly."""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format.")
        if User.query.filter_by(email=email).first():
            raise ValueError("Email already exists.")
        return email

    def set_password(self, password):
        """Hash the password before storing it"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check hashed password"""
        return bcrypt.check_password_hash(self.password_hash, password)  
    
class Space(db.Model):
    __tablename__ = 'spaces'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Boolean)
    image_path = db.Column(db.String(200), nullable=True)
    # Relationship: A space can have many bookings
    bookings = db.relationship("Booking", backref="space", lazy=True, cascade="all, delete-orphan")
    

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey("spaces.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)

    @validates('date')
    def validate_date(self, key, value):
        if not value:
            raise ValueError("Booking date is required.")
        return value

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
