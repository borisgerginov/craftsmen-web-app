from app.db import db
from app.models.user import User

def create_user(email: str, password: str, role: str = "customer") -> User:
    u = User(email=email, role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return u

def login(client, email: str, password: str):
    return client.post("/login", data={"email": email, "password": password})

def register(client, email: str, password: str):
    return client.post("/register", data={"email": email, "password": password})

def logout(client):
    return client.post("/logout")