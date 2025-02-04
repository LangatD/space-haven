from flask import Blueprint, jsonify, request
from .models import db, User, Space, ContactMessage, Booking, Membership
from flask_jwt_extended import create_access_token, jwt_required, create_refresh_token, get_jwt_identity, JWTManager
from app.schemas import UserSchema, SpaceSchema, BookingSchema, MembershipSchema, ContactMessageSchema
from marshmallow import ValidationError
from app import bcrypt
import re
from datetime import datetime
from sqlalchemy.orm import joinedload
bp = Blueprint("api", __name__)  # Define a Flask Blueprint

user_schema = UserSchema()
users_schema = UserSchema(many=True)
space_schema = SpaceSchema()
spaces_schema = SpaceSchema(many=True)
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)
membership_schema = MembershipSchema()
memberships_schema = MembershipSchema(many=True)
contact_schema = ContactMessageSchema()
contacts_schema = ContactMessageSchema(many=True)

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
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify({"access_token": access_token, "refresh_token": refresh_token, "user_id": user.id}), 200
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

    return jsonify(user_schema.dump(user))

@bp.route("/api/users/<int:user_id>/bookings", methods=["GET"])
@jwt_required()
def get_user_bookings(user_id):
    if get_jwt_identity() != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    bookings = Booking.query.filter_by(user_id=user_id).all()
    #return jsonify(bookings_schema.dump(bookings)), 200
    
    booking_list = []
    for booking in bookings:
        booking_list.append({
            "id": booking.id,
            "date": booking.date.strftime('%b %d %Y, %I:%M %p'),
            "space": {
                "id": booking.space.id,
                "name": booking.space.name,
                "image_path": booking.space.image_path
            }
        })

    return jsonify(booking_list), 200
@bp.route("/api/spaces", methods=["GET"])
def get_spaces():
    try:
        spaces = Space.query.all()
        return jsonify(spaces_schema.dump(spaces))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/spaces/<int:space_id>', methods=['GET'])
def get_space(space_id):
    try:
        space = Space.query.get_or_404(space_id)
        return jsonify(space_schema.dump(space)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    try:
        data = request.get_json()
        required_fields = ['space_id', 'date']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        new_booking = Booking(
            user_id=get_jwt_identity(),
            space_id=data['space_id'],
            date=datetime.fromisoformat(data['date'])
        )
        db.session.add(new_booking)
        db.session.commit()
        
        return jsonify({
            "message": "Booking created",
            "booking_id": new_booking.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@bp.route("/api/memberships", methods=["GET"])
def get_memberships():
    memberships = Membership.query.all()
    return jsonify(memberships_schema.dump(memberships)), 200

@bp.route('/api/users/<int:user_id>/membership', methods=['PUT'])
@jwt_required()
def update_membership(user_id):
    try:
        if get_jwt_identity() != user_id:
            return jsonify({"error": "Unauthorized"}), 403
            
        data = request.get_json()
        user = User.query.options(joinedload(User.membership)).get(user_id)
        membership = Membership.query.get(data['membership_id'])
        
        if not membership:
            return jsonify({"error": "Invalid membership"}), 400
            
        user.membership = membership
        db.session.commit()
        
        return jsonify({
            "message": "Membership updated",
            "user": user_schema.dump(user),
            "membership": membership_schema.dump(membership)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@bp.route("/api/contact", methods=["POST"])
def contact_support():
    try:
        data = request.get_json()
        new_message = ContactMessage(
            name=data["name"],
            email=data["email"],
            message=data["message"]
        )

        db.session.add(new_message)
        db.session.commit()
        return jsonify(contact_schema.dump(new_message)), 201  # ✅ Return structured response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/test_db", methods=["GET"])
def test_db():
    try:
        user = User.query.first()
        return jsonify({"message": "Connected to Supabase!", "first_user": user.name if user else "No users found"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)  # 👈 Requires a valid refresh token
def refresh_token():
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)
    return jsonify({"access_token": new_access_token})