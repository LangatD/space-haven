import json
from sqlalchemy import inspect 
from app import create_app, db
from app.models import Space, Membership

app = create_app()

with app.app_context():
   
    db.create_all()

    # Load data from JSON file
    with open("data.json") as file:
        data = json.load(file)

    
    inspector = inspect(db.engine)
    
    if inspector.has_table("spaces"):
        db.session.query(Space).delete()
    if inspector.has_table("memberships"):
        db.session.query(Membership).delete()

    # Add spaces
    spaces = [Space(**space) for space in data["spaces"]]
    db.session.add_all(spaces)

    # Add memberships
    memberships = [Membership(**membership) for membership in data["memberships"]]
    db.session.add_all(memberships)

    db.session.commit()
