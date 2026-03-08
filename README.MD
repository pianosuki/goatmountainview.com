![Logo](/app/static/images/simple_things.png)

# Goat Mountain View

Copyediting and Nigerian Dwarf Goats in Washington.

## Prerequisites

- Python 3.11
- Docker & Docker Compose (for production deployment)

## Installation

### Option 1: Local Development

1. Clone the repository: `git clone https://github.com/pingosuki/goatmountainview.com.git`
2. Navigate to the project directory: `cd goatmountainview.com`
3. Create a virtual environment: `python3 -m venv venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Install the dependencies: `pip install -r requirements.txt`

#### Configuration

1. Create the file `.env` and set the following variables:
   - `SECRET_KEY=<your-secret-key>`
   - `USERNAME=<your-username>`
   - `PASSWORD=<your-password>`
2. Run the setup function to generate the database: `python main.py`

#### Running the project

1. Run the website via your WSGI HTTP server of choice: `gunicorn main:app`

---

### Option 2: Docker Deployment (Recommended for Production)

This method ensures your uploaded images and database persist across deployments.

#### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pingosuki/goatmountainview.com.git
   cd goatmountainview.com
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d --build
   ```

4. **Access the website:**
   - Open your browser to `http://localhost:8000`
   - Login at `http://localhost:8000/login`

#### Docker Commands

```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose down

# View logs
docker-compose logs -f

# Restart after code changes
docker-compose restart

# Rebuild after Dockerfile changes
docker-compose up -d --build
```

#### Data Persistence

Your data is automatically persisted in Docker volumes:
- **`goatmountainview_uploads`**: All uploaded images
- **`goatmountainview_instance`**: SQLite database

**Important:** These volumes persist even if you remove the container. To backup your data:

```bash
# Backup uploads
docker run --rm -v goatmountainview_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads-backup.tar.gz /data

# Backup database
docker run --rm -v goatmountainview_instance:/data -v $(pwd):/backup alpine tar czf /backup/database-backup.tar.gz /data
```

---

## Admin Panel Guide

### Accessing the Admin Panel

1. Navigate to `/admin` or click the "Admin" button on the website
2. Login with your credentials from the `.env` file
3. You'll see the admin dashboard with all content sections

### Managing Images

**To upload a new image:**

1. Click on "Images" in the admin dashboard
2. In the "Add New Record" form on the right:
   - Click or drag to upload your image
   - Optionally add a folder name (e.g., "does", "soap", "adoptions")
   - Add a note if desired
3. Click "Add Record"
4. ✅ Your image is now live on the website!

**To replace an existing image:**

1. Find the image in the table
2. Click "Edit"
3. Scroll to the "Replace Image" section
4. Upload your new image
5. Click "Save Changes"
6. ✅ The image is updated everywhere on the site!

### Managing Goats (Does & Foundation)

**To add a new goat:**

1. Click on "Does" or "Foundation Goats"
2. Fill in the form:
   - **Name**: The goat's name (creates a new goat entry)
   - **Description**: Information about the goat
   - **Link**: Optional pedigree or registration link
   - **Image**: Upload a photo (required)
3. Click "Add Record"
4. ✅ Your goat is now displayed on the website!

### Managing Soaps

**To add a new soap product:**

1. Click on "Soaps"
2. Fill in the form:
   - **Name**: Product name
   - **Ingredients**: List of ingredients
   - **Weight**: Weight in ounces/grams
   - **Image**: Upload a product photo
3. Click "Add Record"
4. ✅ Your soap product is now listed!

### Tips for Non-Technical Users

- 📷 **Image Format**: Use JPG or PNG files for best compatibility
- 📁 **Organize Images**: Use folder names like "does", "soap", "adoptions" to keep images organized
- ✏️ **Edit Anytime**: Click "Edit" on any record to update information
- 🗑️ **Delete Safely**: Confirm before deleting - this removes both the record and associated images
- 💾 **Auto-Save**: All changes are saved immediately and appear on the website right away
- 🔄 **Replace Images**: You can replace an image without changing the filename - perfect for updating photos!

---

## Troubleshooting

### Images not showing after deployment

If you're using Docker, your images should persist automatically. Check:

```bash
# Verify volumes are mounted
docker-compose ps
docker volume ls | grep goatmountainview
```

### Database errors on first run

Make sure your `.env` file exists with proper values:

```bash
# Check .env file
cat .env
```

### Can't access admin panel

1. Ensure you've run the setup (automatic with Docker on first run)
2. Verify your credentials in the `.env` file
3. Check the application logs: `docker-compose logs`

---

## Project Structure

```
goatmountainview.com/
├── app/
│   ├── static/          # CSS, JS, and uploaded images
│   ├── templates/       # HTML templates
│   ├── models.py        # Database models
│   ├── routes.py        # Web routes
│   └── crud.py          # Database operations
├── instance/            # SQLite database (persisted in Docker)
├── docker-compose.yml   # Docker configuration
├── Dockerfile          # Build instructions
└── .env                # Environment variables (create this)
```

---

## Support

For issues or questions, please open an issue on GitHub or contact the administrator.
