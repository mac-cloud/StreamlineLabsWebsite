# test_app.py - Comprehensive test suite for Streamline Labs Flask app

import pytest
import json
from unittest.mock import patch, MagicMock
from app import app, db, ContactMessage
import tempfile
import os

# Test configuration
@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    # Create a temporary database for testing
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory SQLite for tests
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

@pytest.fixture
def sample_contact_data():
    """Sample contact form data for testing"""
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'message': 'I need help with my business website'
    }

class TestContactAPI:
    """Test cases for contact form functionality"""
    
    def test_home_page_loads(self, client):
        """Test that the home page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Streamline Labs' in response.data
    
    def test_health_check(self, client):
        """Test the health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_contact_form_valid_submission(self, client, sample_contact_data):
        """Test successful contact form submission"""
        with patch('app.send_notification_email') as mock_email:
            response = client.post('/api/contact', 
                                 json=sample_contact_data,
                                 headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'Thank you for your message' in data['message']
            assert 'id' in data
            
            # Verify database entry
            message = ContactMessage.query.get(data['id'])
            assert message is not None
            assert message.name == sample_contact_data['name']
            assert message.email == sample_contact_data['email']
            
            # Verify email was attempted to be sent
            mock_email.assert_called_once()
    
    def test_contact_form_missing_data(self, client):
        """Test contact form with missing required fields"""
        test_cases = [
            {},  # Empty data
            {'name': 'John'},  # Missing email and message
            {'name': 'John', 'email': 'john@example.com'},  # Missing message
            {'email': 'john@example.com', 'message': 'Hello'},  # Missing name
        ]
        
        for data in test_cases:
            response = client.post('/api/contact', 
                                 json=data,
                                 headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 400
            response_data = json.loads(response.data)
            assert 'error' in response_data
    
    def test_contact_form_invalid_email(self, client):
        """Test contact form with invalid email formats"""
        invalid_emails = [
            'notanemail',
            'missing@domain',
            '@missinguser.com',
            'spaces in@email.com',
            'multiple@@signs.com'
        ]
        
        for email in invalid_emails:
            data = {
                'name': 'Test User',
                'email': email,
                'message': 'Test message'
            }
            
            response = client.post('/api/contact', 
                                 json=data,
                                 headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 400
            response_data = json.loads(response.data)
            assert 'valid email' in response_data['error'].lower()
    
    def test_contact_form_no_json_data(self, client):
        """Test contact form with no JSON data"""
        response = client.post('/api/contact')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'No data provided' in data['error']
    
    def test_contact_form_whitespace_handling(self, client):
        """Test that form handles whitespace properly"""
        data = {
            'name': '  John Doe  ',
            'email': '  john@example.com  ',
            'message': '  Test message  '
        }
        
        with patch('app.send_notification_email'):
            response = client.post('/api/contact', 
                                 json=data,
                                 headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 200
            # Verify trimmed data was saved
            response_data = json.loads(response.data)
            message = ContactMessage.query.get(response_data['id'])
            assert message.name == 'John Doe'
            assert message.email == 'john@example.com'
            assert message.message == 'Test message'

class TestDatabaseOperations:
    """Test database-related functionality"""
    
    def test_contact_message_creation(self, client):
        """Test ContactMessage model creation"""
        message = ContactMessage(
            name='Test User',
            email='test@example.com',
            message='Test message',
            ip_address='127.0.0.1'
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Verify the message was saved
        saved_message = ContactMessage.query.first()
        assert saved_message is not None
        assert saved_message.name == 'Test User'
        assert saved_message.email == 'test@example.com'
        assert saved_message.is_read is False
    
    def test_contact_message_to_dict(self, client):
        """Test ContactMessage to_dict method"""
        message = ContactMessage(
            name='Test User',
            email='test@example.com',
            message='Test message'
        )
        
        db.session.add(message)
        db.session.commit()
        
        message_dict = message.to_dict()
        assert message_dict['name'] == 'Test User'
        assert message_dict['email'] == 'test@example.com'
        assert message_dict['message'] == 'Test message'
        assert 'created_at' in message_dict
        assert 'id' in message_dict

class TestMessageManagement:
    """Test message management endpoints"""
    
    def test_get_messages_empty(self, client):
        """Test getting messages when database is empty"""
        response = client.get('/api/messages')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['messages'] == []
        assert data['total'] == 0
    
    def test_get_messages_with_data(self, client):
        """Test getting messages with data in database"""
        # Create test messages
        for i in range(5):
            message = ContactMessage(
                name=f'User {i}',
                email=f'user{i}@example.com',
                message=f'Message {i}'
            )
            db.session.add(message)
        db.session.commit()
        
        response = client.get('/api/messages')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['messages']) == 5
        assert data['total'] == 5
    
    def test_mark_message_as_read(self, client):
        """Test marking a message as read"""
        # Create a test message
        message = ContactMessage(
            name='Test User',
            email='test@example.com',
            message='Test message'
        )
        db.session.add(message)
        db.session.commit()
        
        # Mark as read
        response = client.put(f'/api/messages/{message.id}/read')
        assert response.status_code == 200
        
        # Verify it was marked as read
        updated_message = ContactMessage.query.get(message.id)
        assert updated_message.is_read is True

class TestEmailFunctionality:
    """Test email-related functionality"""
    
    @patch('app.mail.send')
    def test_email_sending_success(self, mock_send, client, sample_contact_data):
        """Test that emails are sent successfully"""
        response = client.post('/api/contact', 
                             json=sample_contact_data,
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200
        # Verify that mail.send was called twice (admin + customer emails)
        assert mock_send.call_count == 2
    
    @patch('app.mail.send')
    def test_email_sending_failure_graceful(self, mock_send, client, sample_contact_data):
        """Test that email failures are handled gracefully"""
        mock_send.side_effect = Exception("Email server error")
        
        response = client.post('/api/contact', 
                             json=sample_contact_data,
                             headers={'Content-Type': 'application/json'})
        
        # Should still return success even if email fails
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_404_error_handler(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Endpoint not found' in data['error']
    
    def test_database_error_simulation(self, client):
        """Test handling of database errors"""
        with patch('app.db.session.commit') as mock_commit:
            mock_commit.side_effect = Exception("Database error")
            
            response = client.post('/api/contact', 
                                 json={'name': 'Test', 'email': 'test@example.com', 'message': 'Test'},
                                 headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'Something went wrong' in data['error']

# Debugging with PDB - Example usage
def debug_contact_submission():
    """
    Example function showing how to use pdb for debugging
    Run this with: python -c "from test_app import debug_contact_submission; debug_contact_submission()"
    """
    import pdb
    
    # Sample data for debugging
    test_data = {
        'name': 'Debug User',
        'email': 'debug@example.com',
        'message': 'This is a debug message'
    }
    
    # Set breakpoint here
    pdb.set_trace()
    
    # You can now inspect variables, step through code, etc.
    # Common pdb commands:
    # n (next line)
    # s (step into function)
    # c (continue)
    # l (list current code)
    # p variable_name (print variable)
    # pp variable_name (pretty print)
    # q (quit)
    
    print(f"Processing contact data: {test_data}")
    
    # Simulate processing
    if test_data['email'] and '@' in test_data['email']:
        print("Email validation passed")
    else:
        print("Email validation failed")

# Performance testing with manual timing
def test_contact_form_performance(client, sample_contact_data):
    """Test contact form response time"""
    import time
    
    start_time = time.time()
    
    with patch('app.send_notification_email'):
        response = client.post('/api/contact', 
                             json=sample_contact_data,
                             headers={'Content-Type': 'application/json'})
    
    end_time = time.time()
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 1.0  # Should respond within 1 second
    print(f"Contact form response time: {response_time:.3f} seconds")

# Integration test example
def test_full_contact_flow_integration(client):
    """Integration test for the complete contact flow"""
    import pdb
    
    # You can add pdb.set_trace() at any point to debug
    # pdb.set_trace()
    
    contact_data = {
        'name': 'Integration Test User',
        'email': 'integration@test.com',
        'message': 'This is an integration test message that should trigger the full flow'
    }
    
    # Submit contact form
    with patch('app.send_notification_email') as mock_email:
        response = client.post('/api/contact', 
                             json=contact_data,
                             headers={'Content-Type': 'application/json'})
    
    # Verify successful submission
    assert response.status_code == 200
    data = json.loads(response.data)
    message_id = data['id']
    
    # Verify message was saved to database
    saved_message = ContactMessage.query.get(message_id)
    assert saved_message is not None
    assert saved_message.is_read is False
    
    # Test retrieving messages
    response = client.get('/api/messages')
    assert response.status_code == 200
    messages_data = json.loads(response.data)
    assert len(messages_data['messages']) == 1
    
    # Test marking as read
    response = client.put(f'/api/messages/{message_id}/read')
    assert response.status_code == 200
    
    # Verify it was marked as read
    updated_message = ContactMessage.query.get(message_id)
    assert updated_message.is_read is True

# Custom debugging decorator
def debug_route(func):
    """Decorator to add debugging to Flask routes"""
    def wrapper(*args, **kwargs):
        print(f"🐛 DEBUG: Entering {func.__name__}")
        print(f"🐛 DEBUG: Args: {args}")
        print(f"🐛 DEBUG: Kwargs: {kwargs}")
        
        # Uncomment the next line to set a breakpoint
        # import pdb; pdb.set_trace()
        
        result = func(*args, **kwargs)
        print(f"🐛 DEBUG: Exiting {func.__name__}")
        return result
    return wrapper

# Example of using the debugging decorator
# Apply this to your routes in app.py like:
# @app.route('/api/contact', methods=['POST'])
# @debug_route
# def submit_contact():
#     # your existing code here

if __name__ == '__main__':
    # Run tests with: python test_app.py
    pytest.main([__file__, '-v'])