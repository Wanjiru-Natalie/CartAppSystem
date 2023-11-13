from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from flask_session import Session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from config import ApplicationConfig
from models import *
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(ApplicationConfig)

bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
server_session = Session(app)
db.init_app(app)
migrate = Migrate(app, db)

# Configure JWT
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a secret key for production
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

@app.route("/@me")
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = Contacts.query.filter_by(id=current_user_id).first()
    return jsonify(user.profile())

@app.route("/register", methods=["POST"])
def register_user():
    email = request.json["email"]
    password = request.json["password"]
    first_name =request.json["first_name"]
    last_name = request.json["last_name"]
    username = request.json["username"]
    phone_number = request.json["phone_number"]
    picture =request.json["profile_picture_url"]

    user_exists = Contacts.query.filter_by(email=email).first() 

    if picture:
        profile_picture_url = picture
    else:
        # Generate alternate profile picture URL with initials
        profile_picture_url = Contacts.generate_profile_picture_url()

    if user_exists:
        return jsonify({"error": "User already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password)
    new_user = Contacts(first_name=first_name, last_name=last_name, username=username, phone_number=phone_number, profile_picture_url=profile_picture_url,email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # Create JWT token and include it in the response
    access_token = create_access_token(identity=new_user.id)
    return jsonify(access_token=access_token, id=new_user.id, email=new_user.email)


@app.route("/login", methods=["POST"])
def login_user():
    email = request.json["email"]
    password = request.json["password"]

    user = Contacts.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401

    # Create JWT token and include it in the response
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token, id=user.id, email=user.email)

@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id")
    return "200"

if __name__ == "__main__":
    app.run(debug=True)
