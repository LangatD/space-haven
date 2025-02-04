import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret")
    jwt = JWTManager(app)
    print("Database URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))  # Debugging

    CORS(app,resources={r"/api/*": {"origins": ["https://space-haven-react.vercel.app/"]}}, supports_credentials=True)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    
    from app import models  

    with app.app_context():
        from .routes import bp as routes_blueprint
        app.register_blueprint(routes_blueprint)

    return app
