from flask import Blueprint, jsonify, request
from .models import db, User, Space, Booking, Membership
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from app.schemas import UserSchema
from marshmallow import ValidationError
from app import bcrypt
import re

bp = Blueprint("api", __name__)  # Define a Flask Blueprint

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@bp.route('/')
def home():
    return jsonify({"message": "Welcome to the Space Haven API!"})

# User Registration

@bp.route("/api/users", methods=["POST"])
def register_user():
    try:
        data = request.get_json()
        if "name" not in data or "email" not in data or "password" not in data:
            return jsonify({"error": "Missing required fields."}), 400
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
            return jsonify({"error": "Invalid email format"}), 400
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email already exists"}), 409

        # ✅ Hash password properly
        new_user = User(
            name=data["name"],
            email=data["email"],
            password_hash=bcrypt.generate_password_hash(data["password"]).decode('utf-8')  # ✅ Correct way
        )
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data["email"]).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # ✅ Correct password verification
        if not bcrypt.check_password_hash(user.password_hash, data["password"]):
            return jsonify({"error": "Invalid password"}), 401

        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token, "user_id": user.id}), 200
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@bp.route("/api/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    current_user_id = get_jwt_identity()  # ✅ Get user ID from JWT
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "membership": user.membership if user.membership else "None"
    })

@bp.route("/api/spaces", methods=["GET"])
def get_spaces():
    spaces = Space.query.all()
    return jsonify([{
        "id": space.id,
        "name": space.name,
        "location": space.location,
        "price": space.price,
        "availability": space.availability
    } for space in spaces])

@bp.route("/api/bookings", methods=["POST"])
def create_booking():
    data = request.get_json()
    new_booking = Booking(
        user_id=data["user_id"],
        space_id=data["space_id"],
        booking_date=data["booking_date"]
    )
    db.session.add(new_booking)
    db.session.commit()
    return jsonify({"message": "Booking created successfully"}), 201

@bp.route("/api/memberships", methods=["GET"])
def get_memberships():
    memberships = Membership.query.all()
    return jsonify([{
        "id": membership.id,
        "name": membership.name,
        "price": membership.price,
        "benefits": membership.benefits
    } for membership in memberships])

@bp.route("/api/contact", methods=["POST"])
def contact_support():
    data = request.get_json()
    return jsonify({"message": "Your message has been sent"}), 200

@bp.route("/api/test_db", methods=["GET"])
def test_db():
    try:
        user = User.query.first()
        return jsonify({"message": "Connected to Supabase!", "first_user": user.name if user else "No users found"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
