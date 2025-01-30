from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

import re
from app import db, bcrypt


# ------------------------------
# ✅ Membership Model (Fix: Explicit Foreign Key)
# ------------------------------
class Membership(db.Model):
    __tablename__ = 'memberships'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    features = db.Column(db.Text, nullable=True)

    # Relationship: One Membership → Many Users
    users = db.relationship("User", backref="membership", lazy=True)

# ------------------------------
# ✅ User Model (Fix: Add `membership_id` Foreign Key)
# ------------------------------
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)  # ✅ Store hashed password correctly
    membership_id = db.Column(db.Integer, db.ForeignKey("memberships.id"), nullable=True)  # Foreign Key

    # Relationship: One user can have many bookings
    bookings = db.relationship("Booking", backref="user", lazy=True, cascade="all, delete-orphan")

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
        return bcrypt.check_password_hash(self.password_hash, password)  # ✅ Correct password check

# ------------------------------
# ✅ Space Model (Coworking Spaces)
# ------------------------------
class Space(db.Model):
    __tablename__ = 'spaces'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Boolean)
    # Relationship: A space can have many bookings
    bookings = db.relationship("Booking", backref="space", lazy=True, cascade="all, delete-orphan")

# ------------------------------
# ✅ Booking Model (Reservations)
# ------------------------------
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
