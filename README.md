# Streamline Labs - Flask Backend Setup Guide

## Prerequisites

1. **Python 3.8+** installed on your system
2. **MySQL Server** installed and running
3. **Gmail account** with App Password enabled

## Step 1: Set up MySQL Database

1. Install MySQL if you haven't already:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# macOS (using Homebrew)
brew install mysql

# Windows: Download from https://dev.mysql.com/downloads/mysql/
```

2. Start MySQL service:
```bash
# Ubuntu/Debian
sudo systemctl start mysql

# macOS
brew services start mysql

# Windows: Use MySQL Workbench or start from Services
```

3. Login to MySQL and create the database:
```bash
mysql -u root -p
```

4. Run the SQL setup script (from the MySQL Setup artifact):
```sql
CREATE DATABASE IF NOT EXISTS streamline_labs;
USE streamline_labs;

CREATE TABLE IF NOT EXISTS contact_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    ip_address VARCHAR(45),
    INDEX idx_created_at (created_at),
    INDEX idx_is_read (is_read),
    INDEX idx_email (email)
);
```

## Step 2: Set up Gmail App Password

1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. At the bottom, click "App passwords"
4. Select "Mail" and your device
5. Copy the generated 16-character password

## Step 3: Install Python Dependencies

1. Create a new directory for your project:
```bash
mkdir streamline-labs-backend
cd streamline-labs-backend
```

2. Create a virtual environment:
```bash
python -m venv venv

# Activate it:
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables

1. Create a `.env` file in your project root:
```bash
touch .env
```

2. Add your configuration (update with your actual values):
```env
# Database Configuration
DATABASE_URL=mysql://root:your_mysql_password@localhost/streamline_labs

# Email Configuration
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_16_character_app_password
ADMIN_EMAIL=infostreamlinelabs@gmail.com

# Security
SECRET_KEY=your-very-secret-random-key-here
```

## Step 5: Run the Flask Application

1. Save the Flask backend code as `app.py`
2. Run the application:
```bash
python app.py
```

You should see:
```
Database tables created successfully!
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[your-ip]:5000
```

## Step 6: Update Your HTML File

1. Replace your current HTML file with the updated version
2. Make sure the `API_BASE_URL` in the JavaScript matches your Flask server URL
3. If running locally, it should be `http://localhost:5000/api`

## Step 7: Test the Contact Form

1. Open your HTML file in a browser
2. Fill out the contact form
3. Submit it
4. Check:
   - You should see a success message on the website
   - You should receive an email notification
   - The customer should receive an auto-reply
   - Data should be saved in the MySQL database

## API Endpoints

- `POST /api/contact` - Submit contact form
- `GET /api/messages` - Get all messages (for admin dashboard)
- `PUT /api/messages/<id>/read` - Mark message as read
- `GET /api/health` - Health check

## Troubleshooting

### Database Connection Issues
```bash
# Check if MySQL is running
sudo systemctl status mysql

# Test connection
mysql -u root -p -e "SHOW DATABASES;"
```

### Email Issues
- Make sure 2FA is enabled on your Gmail account
- Use App Password, not your regular Gmail password
- Check that Gmail allows "Less secure app access" if needed

### CORS Issues
If you get CORS errors, make sure Flask-CORS is installed and the frontend URL is correct.

### Testing Database Connection
```python
# Test script (save as test_db.py)
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='your_password',
        database='streamline_labs'
    )
    print("Database connection successful!")
    conn.close()
except Exception as e:
    print(f"Database connection failed: {e}")
```

## Production Deployment

For production:

1. **Use a production WSGI server** like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **Set up a reverse proxy** with Nginx
3. **Use environment variables** for sensitive data
4. **Enable SSL/HTTPS**
5. **Set up database backups**
6. **Monitor logs** for errors

## File Structure
```
streamline-labs-backend/
├── app.py
├── requirements.txt
├── .env
├── .env.example
└── README.md
```

## Security Notes

- Never commit `.env` files to version control
- Use strong, unique passwords for database
- Regularly update dependencies
- Implement rate limiting for production
- Use HTTPS in production
- Validate and sanitize all user inputs

Your contact form is now fully functional with email notifications and database storage!