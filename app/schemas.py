from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from app.models import User, Space, Booking, Membership, ContactMessage

class UserSchema(SQLAlchemyAutoSchema):
    membership_id = fields.Integer()
    class Meta:
        model = User
        load_instance = True
        include_fk = True
    password_hash = fields.String(load_only=True)  # Exclude from responses

class SpaceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Space
        load_instance = True

class BookingSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Booking
        load_instance = True

class MembershipSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Membership
        load_instance = True
        include_fk = True


class ContactMessageSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ContactMessage
        load_instance = True

