# Streamline Labs Website

!(static/image1.png)
!(static/image2.png)
!(static/image3.png)
!(static/image4.png)

A modern, responsive website for Streamline Labs - a digital solutions company helping small businesses in Nairobi work smarter through technology.

## 🚀 Features

### Frontend
- **Responsive Design**: Mobile-first approach with modern CSS Grid and Flexbox
- **Interactive UI**: Smooth animations, hover effects, and scroll-based interactions
- **Contact Form**: Client-side validation with real-time feedback
- **SEO Optimized**: Structured data, meta tags, and semantic HTML
- **Performance**: Optimized images, CSS animations, and fast loading

### Backend
- **Flask REST API**: Clean API endpoints for contact form submissions
- **Database Integration**: MySQL with SQLAlchemy ORM
- **Email Notifications**: Automated email responses using Flask-Mail
- **Data Validation**: Server-side validation for all form inputs
- **CORS Support**: Cross-origin resource sharing enabled
- **Error Handling**: Comprehensive error handling and logging

## 🛠 Tech Stack

- **Backend**: Python Flask
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Email**: Flask-Mail with Gmail SMTP
- **Styling**: Custom CSS with CSS Grid, Flexbox, and animations
- **Deployment**: Ready for production deployment

## 📦 Installation

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Gmail account for email notifications

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd streamline-labs-website
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask flask-sqlalchemy flask-cors flask-mail python-dotenv mysql-connector-python
   ```

4. **Database Setup**
   ```sql
   CREATE DATABASE streamline_labs;
   CREATE USER 'streamline_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON streamline_labs.* TO 'streamline_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

5. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your_secret_key_here
   DATABASE_URL=mysql://streamline_user:your_password@localhost/streamline_labs
   MAIL_USERNAME=your_gmail@gmail.com
   MAIL_PASSWORD=your_app_password
   ADMIN_EMAIL=infostreamlinelabs@gmail.com
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the website**
   Open your browser and navigate to `http://localhost:5000`

## 📁 Project Structure

```
streamline-labs-website/
├── app.py                 # Main Flask application
├── templates/
│   └── Index.html        # Main website template
├── static/
│   └── logo.jpeg         # Company logo
├── .env                  # Environment variables (create this)
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `DATABASE_URL` | MySQL database connection string | Yes |
| `MAIL_USERNAME` | Gmail account for sending emails | Yes |
| `MAIL_PASSWORD` | Gmail app password | Yes |
| `ADMIN_EMAIL` | Email to receive contact notifications | Yes |

### Gmail Setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: Google Account > Security > App passwords
3. Use the app password in your `.env` file

## 📊 Database Schema

### ContactMessage Table
```sql
CREATE TABLE contact_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    ip_address VARCHAR(45)
);
```

## 🔗 API Endpoints

### POST `/api/contact`
Submit a contact form message
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "message": "I need help with my business website"
}
```

### GET `/api/messages`
Retrieve contact messages (admin only)
- Query parameters: `page`, `per_page`

### PUT `/api/messages/<id>/read`
Mark a message as read

### GET `/api/health`
Health check endpoint

## 🎨 Design Features

- **Modern Gradient Design**: Blue and aqua color scheme
- **Glassmorphism Effects**: Backdrop blur and transparency
- **Smooth Animations**: CSS transitions and keyframe animations
- **Mobile Responsive**: Breakpoints for all device sizes
- **Interactive Elements**: Hover effects and scroll animations

## 🚀 Deployment

### Production Considerations

1. **Environment Setup**
   - Set `debug=False` for production
   - Use environment variables for all sensitive data
   - Configure proper SSL certificates

2. **Database**
   - Use production MySQL instance
   - Set up database backups
   - Configure connection pooling

3. **Email**
   - Consider using dedicated email service (SendGrid, Mailgun)
   - Set up proper SPF/DKIM records

4. **Security**
   - Use HTTPS in production
   - Implement rate limiting
   - Add input sanitization
   - Configure CORS properly

### Deployment Options
- **VPS/Cloud**: Ubuntu with Nginx + Gunicorn
- **Platform-as-a-Service**: Heroku, DigitalOcean App Platform
- **Serverless**: AWS Lambda with Zappa

## 📧 Contact Form Features

- **Real-time Validation**: Instant feedback on form inputs
- **Email Notifications**: Automated emails to both admin and customer
- **Error Handling**: Graceful error messages and retry logic
- **Loading States**: Visual feedback during form submission
- **Responsive Design**: Works perfectly on all devices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📝 License

This project is proprietary software owned by Streamline Labs.

## 📞 Support

- **Email**: infostreamlinelabs@gmail.com
- **Location**: Kasarani Road, Nairobi (Next to Powerstar Supermarket)

## 🔮 Future Enhancements

- [ ] Admin dashboard for message management
- [ ] Customer portal for project tracking
- [ ] Payment integration for services
- [ ] Blog/content management system
- [ ] Multi-language support (English/Swahili)
- [ ] WhatsApp integration
- [ ] Service booking system

---

**Built with ❤️ in Nairobi by Streamline Labs**

*Helping businesses work smarter, not hard.*