# Editor Melinda

Copyediting and Nigerian Dwarf Goats in Washington.

## Prerequisites

- `requirements.txt`

## Installation

1. Clone the repository: `git clone https://github.com/pianosuki/editormelinda.com.git`
2. Navigate to the project directory: `cd editormelinda.com`
3. Create a virtual environment: `python3 -m venv venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Install the dependencies: `pip install -r requirements.txt`
6. Run the setup function by manually launching main.py: `python main.py`

## Running the project

1. Create the file `.env` and set the following variables:
   - `SECRET_KEY=<your-secret-key>`
   - `USERNAME=<your-username>`
   - `PASSWORD=<your-password>`
2. Run the website via your WSGI HTTP server of choice: `gunicorn main:app`
