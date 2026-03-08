"""
Book Models

Represents books in the portfolio (HS and ST categories).
"""

from app import db


class BookHS(db.Model):
    """Book model for HS category."""
    
    __tablename__ = "books_hs"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    editors = db.Column(db.Text(), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<BookHS {self.name}>'


class BookST(db.Model):
    """Book model for ST category."""
    
    __tablename__ = "books_st"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    editors = db.Column(db.Text(), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<BookST {self.name}>'
