"""
Adoption Model

Represents goats available for adoption.
"""

from app import db


class Adoption(db.Model):
    """Adoption model for goats available for adoption."""
    
    __tablename__ = "adoptions"
    
    id = db.Column(db.Integer, primary_key=True)
    goat_id = db.Column(db.Integer, db.ForeignKey("goats.id"), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey("images.id"), default=2)
    
    # Relationships
    goat = db.relationship("Goat", backref="adoption", foreign_keys="Adoption.goat_id")
    image = db.relationship("Image", backref="adoption", foreign_keys="Adoption.image_id")
    
    def __repr__(self):
        return f'<Adoption {self.goat.name if self.goat else "Unknown"}>'
