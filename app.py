from flask import Flask , request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail, Message
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv 

#load env variables
load_dotenv()

app = Flask(__name__)

#configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:1234567890@localhost/streamline_labs')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# email configuration

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

# initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)
CORS(app, resources={r"/*": {"origins": "*"}})


#database model
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(45))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'is_read': self.is_read,
            'ip_address': self.ip_address,
        }

# routes
@app.route('/')
def home():
    return render_template('Index.html')

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    try:
        #get fofrm data
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        message = data.get('message', '').strip()

        #validation
        if not name or not email or not message:
            return jsonify({'error': 'All fields are required'}), 400
        
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Please provide a valid email address'}), 400
        
        # get client ip
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()

            #save to database
            contact_message = ContactMessage(
                name = name,
                email = email,
                message = message,
                ip_address = client_ip
            )

            db.session.add(contact_message)
            db.session.commit()

            #send email notification
            try:
                send_notification_email(contact_message)
            except Exception as e:
                print (f"Email sending Failed: {str(e)}")

                return jsonify({
                'success': True,
                'message': 'Thank you for your message! We\'ll get back to you within 24 hours.',
                'id': contact_message.id
                }), 200 
            return jsonify({
                'success': True,
                'message': 'Thank you for your message! We\'ll get back to you within 24 hours.',
                'id': contact_message.id
            }), 200
    except Exception as e:
                print (f"Error: {str(e)}")
                return jsonify({'error': 'Something went wrong. Please try again later'}), 500


def send_notification_email(contact_message):
    """Send email notification when new contat message is received"""

    #email to business owner
    admin_msg = Message(
        subject=f'New Contact Form Submission - {contact_message.name}',
        recipients=[os.getenv('ADMIN_EMAIL', 'infostreamlinelabs@gmail.com')],
        html=f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #2563eb, #06b6d4); padding: 30px; text-align: center; color: white;">
                <h2 style="margin: 0;">New Contact Message</h2>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Streamline Labs Website</p>
            </div>
            
            <div style="padding: 30px; background: #f8fafc;">
                <div style="background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px;">
                    <h3 style="color: #2563eb; margin-bottom: 15px;">Contact Details</h3>
                    <p><strong>Name:</strong> {contact_message.name}</p>
                    <p><strong>Email:</strong> {contact_message.email}</p>
                    <p><strong>Date:</strong> {contact_message.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>IP Address:</strong> {contact_message.ip_address or 'Unknown'}</p>
                </div>
                
                <div style="background: white; padding: 25px; border-radius: 10px;">
                    <h3 style="color: #2563eb; margin-bottom: 15px;">Message</h3>
                    <div style="background: #f1f5f9; padding: 20px; border-radius: 8px; line-height: 1.6;">
                        {contact_message.message}
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 25px;">
                    <a href="mailto:{contact_message.email}" 
                       style="background: linear-gradient(135deg, #2563eb, #06b6d4); 
                              color: white; 
                              padding: 12px 25px; 
                              text-decoration: none; 
                              border-radius: 25px; 
                              font-weight: bold;">
                        Reply to {contact_message.name}
                    </a>
                </div>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #64748b; font-size: 14px;">
                <p>This message was sent from your Streamline Labs website contact form.</p>
            </div>
        </div>
        """
    )
     # Auto-reply to customer
    customer_msg = Message(
        subject='Thank you for contacting Streamline Labs',
        recipients=[contact_message.email],
        html=f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #2563eb, #06b6d4); padding: 30px; text-align: center; color: white;">
                <h2 style="margin: 0;">Thank You, {contact_message.name}!</h2>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">We've received your message</p>
            </div>
            
            <div style="padding: 30px; background: #f8fafc;">
                <div style="background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px;">
                    <h3 style="color: #2563eb; margin-bottom: 15px;">What's Next?</h3>
                    <p style="line-height: 1.6; margin-bottom: 15px;">
                        Thank you for reaching out to Streamline Labs! We're excited to learn about your business needs.
                    </p>
                    <p style="line-height: 1.6; margin-bottom: 15px;">
                        Our team will review your message and get back to you within <strong>24 hours</strong> with:
                    </p>
                    <ul style="color: #64748b; line-height: 1.8; margin-left: 20px;">
                        <li>A personalized response to your inquiry</li>
                        <li>Relevant solutions for your business</li>
                        <li>Next steps to get started</li>
                    </ul>
                </div>
                
                <div style="background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px;">
                    <h3 style="color: #2563eb; margin-bottom: 15px;">Your Message Summary</h3>
                    <div style="background: #f1f5f9; padding: 15px; border-radius: 8px; font-style: italic; color: #475569;">
                        "{contact_message.message[:200]}{'...' if len(contact_message.message) > 200 else ''}"
                    </div>
                </div>
                
                <div style="background: white; padding: 25px; border-radius: 10px; text-align: center;">
                    <h3 style="color: #2563eb; margin-bottom: 15px;">Need Immediate Help?</h3>
                    <p style="margin-bottom: 15px;">Feel free to call us directly:</p>
                    <p style="font-size: 18px; font-weight: bold; color: #06b6d4;">0114404621</p>
                    <p style="color: #64748b; font-size: 14px;">Business hours: 8 AM - 6 PM, Monday - Friday</p>
                </div>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #64748b; font-size: 14px;">
                <p><strong>Streamline Labs</strong> - Helping businesses work smarter, not hard</p>
                <p>Kasarani Road, Nairobi | infostreamlinelabs@gmail.com</p>
            </div>
        </div>
        """
    )
    
    mail.send(admin_msg)
    mail.send(customer_msg)

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get all contact messages (for admin dashboard)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'messages': [msg.to_dict() for msg in messages.items],
            'total': messages.total,
            'pages': messages.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<int:message_id>/read', methods=['PUT'])
def mark_as_read(message_id):
    """Mark a message as read"""
    try:
        message = ContactMessage.query.get_or_404(message_id)
        message.is_read = True
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Message marked as read'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)    