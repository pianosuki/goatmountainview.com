from app import app
from setup import setup

if __name__ == "__main__":
    setup()
    app.run(debug=True)