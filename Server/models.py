from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from uuid import uuid4
from datetime import datetime




db = SQLAlchemy()
#Initiates the admin side
admin = Admin()

def get_uuid():
    return uuid4().hex

Base = declarative_base()
metadata = Base.metadata

class Contacts(db.Model):
    __tablename__ = "contacts"
    id = db.Column(db.Integer, primary_key=True, unique=True, default=lambda: str(uuid4()))
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String(345), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    profile_picture_url = db.Column(db.Text, nullable=True, default="")  # Set default to an empty string

    def __repr__(self):
        return f"<User {self.username}>"

    def generate_profile_picture_url(self, background_color="#3498db", text_color="#ffffff"):
        # Generate a URL with initials and background color if no profile picture URL is provided
        if not self.profile_picture_url:
            initials = "".join(part[0].upper() for part in self.email.split("@"))
            return f"https://example.com/profile_pictures/{initials}.jpg?background={background_color}&text={text_color}"
        return self.profile_picture_url
    
    def profile(self):
        return {"id": self.id, 
                "firstName": self.first_name, 
                "lastName": self.last_name,
                "username": self.username,
                "email": self.email,
                "phoneNumber": self.phone_number,
                "profile_picture":self.profile_picture_url}


admin.add_view(ModelView(Contacts,db.session))

   
class Conversations(db.Model):
    __tablename__ = 'conversations'

    conversationId=db.Column(db.Integer, primary_key=True, unique=True, default=lambda: str(uuid4()))
    conversationName=db.Column(db.String,nullable=False)

admin.add_view(ModelView(Conversations,db.session))

class Items(db.Model):
    __tablename__ = 'items'


    itemId=db.Column(db.Integer, primary_key=True, unique=True, default=lambda: str(uuid4()))
    itemName=db.Column(db.String,nullable=False)
    itemQuantity=db.Column(db.Integer,nullable=False)
    senderId=db.Column(db.Integer,db.ForeignKey('contacts.id'),nullable=False)
    conversationId=db.Column(db.Integer,db.ForeignKey('conversations.conversationId'),nullable=False)
    itemTimeStamp=db.Column(db.DateTime,default=datetime.utcnow())
   
   
admin.add_view(ModelView(Items,db.session))

class Conversationmembers(db.Model):
    __tablename__ = "conversationmembers"

    id=db.Column(db.Integer, primary_key=True, unique=True, default=lambda: str(uuid4()))
    conversationId=db.Column(db.Integer,db.ForeignKey('conversations.conversationId'),nullable=False)
    senderId=db.Column(db.Integer,db.ForeignKey('contacts.id'),nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    left_at = db.Column(db.DateTime, nullable=True)

admin.add_view(ModelView(Conversationmembers,db.session))

class Admins(db.Model):
    __tablename__ = "admins"

    adminId=db.Column(db.Integer, primary_key=True, unique=True, default=lambda: str(uuid4()))
    senderId=db.Column(db.Integer,db.ForeignKey('contacts.id'),nullable=False)
    conversationId=db.Column(db.Integer,db.ForeignKey('conversations.conversationId'),nullable=False)

admin.add_view(ModelView(Admins,db.session))
