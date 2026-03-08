"""
Image Model

Represents uploaded images in the system.
"""

from app import db


class Image(db.Model):
    """Image model for storing uploaded photos."""
    
    __tablename__ = "images"
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    directory = db.Column(db.String(100), default="")
    note = db.Column(db.Text())
    goat_id = db.Column(db.Integer, db.ForeignKey("goats.id"))
    soap_id = db.Column(db.Integer, db.ForeignKey("soaps.id"))
    
    @property
    def path(self):
        """Get the full path to the image file."""
        return self.directory + "/" + self.filename if self.directory else self.filename
    
    def __repr__(self):
        return f'<Image {self.filename}>'
