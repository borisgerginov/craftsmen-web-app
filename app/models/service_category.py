from app.db import db

class ServiceCategory(db.Model):
    __tablename__ = "service_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True, index=True)

    def __repr__(self):
        return f"<ServiceCategory {self.name}>"
    
