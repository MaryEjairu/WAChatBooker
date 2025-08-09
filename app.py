import os
import logging
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback_secret_key_for_whatsapp_bot")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///appointments.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Import bot handler after app creation
from bot_handler import handle_whatsapp_message

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook endpoint for receiving WhatsApp messages from Twilio
    """
    try:
        # Get the incoming message data from Twilio
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        
        app.logger.info(f"Received message: '{incoming_msg}' from {from_number}")
        
        # Process the message using our bot handler
        response = handle_whatsapp_message(incoming_msg, from_number)
        
        app.logger.info(f"Sending response: {response}")
        
        # Return TwiML response
        from twilio.twiml.messaging_response import MessagingResponse
        twiml_response = MessagingResponse()
        twiml_response.message(response)
        
        return str(twiml_response)
        
    except Exception as e:
        app.logger.error(f"Error processing webhook: {str(e)}")
        # Return a generic error message
        from twilio.twiml.messaging_response import MessagingResponse
        twiml_response = MessagingResponse()
        twiml_response.message("Sorry, I'm having trouble processing your request. Please try again later.")
        return str(twiml_response)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint
    """
    return {"status": "healthy", "message": "WhatsApp Appointment Bot is running"}

@app.route('/', methods=['GET'])
def index():
    """
    Simple admin dashboard to view appointments
    """
    from models import Appointment
    appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(20).all()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WhatsApp Appointment Bot</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>
            .status-confirmed { color: var(--bs-success); }
            .status-cancelled { color: var(--bs-danger); }
        </style>
    </head>
    <body>
        <div class="container mt-4">
            <div class="row">
                <div class="col-md-12">
                    <h1 class="mb-4">🤖 WhatsApp Appointment Bot Dashboard</h1>
                    
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">📋 Bot Status</h5>
                                    <p class="card-text">
                                        <span class="badge bg-success">✅ Active</span><br>
                                        Ready to receive WhatsApp messages
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">🔗 Webhook URL</h5>
                                    <p class="card-text">
                                        <code>/webhook</code><br>
                                        <small class="text-muted">Configure this in your Twilio Console</small>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">📅 Recent Appointments</h5>
                        </div>
                        <div class="card-body">
    """
    
    if appointments:
        html += """
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Name</th>
                                            <th>Date</th>
                                            <th>Time</th>
                                            <th>Phone</th>
                                            <th>Status</th>
                                            <th>Created</th>
                                        </tr>
                                    </thead>
                                    <tbody>
        """
        
        for apt in appointments:
            from date_utils import format_date_for_display, format_time_for_display
            status_class = "status-confirmed" if apt.status == "confirmed" else "status-cancelled"
            html += f"""
                                        <tr>
                                            <td><strong>{apt.name}</strong></td>
                                            <td>{format_date_for_display(apt.date)}</td>
                                            <td>{format_time_for_display(apt.time)}</td>
                                            <td><small>{apt.phone_number}</small></td>
                                            <td><span class="{status_class}">●</span> {apt.status.title()}</td>
                                            <td><small>{apt.created_at.strftime('%d/%m/%Y %H:%M')}</small></td>
                                        </tr>
            """
        
        html += """
                                    </tbody>
                                </table>
                            </div>
        """
    else:
        html += """
                            <div class="text-center py-4">
                                <p class="text-muted">No appointments yet. Users can start booking through WhatsApp!</p>
                            </div>
        """
    
    html += """
                        </div>
                    </div>
                    
                    <div class="row mt-4">
                        <div class="col-md-12">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">💬 Available Commands</h5>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <h6>📅 Book Appointment</h6>
                                            <code>Book [Name] [DD-MM-YYYY] [HH:MM]</code>
                                            <p class="small text-muted mt-1">Example: Book John Doe 25-08-2025 14:30</p>
                                        </div>
                                        <div class="col-md-6">
                                            <h6>📋 View Appointments</h6>
                                            <code>My appointments</code>
                                            <p class="small text-muted mt-1">Shows all upcoming bookings</p>
                                        </div>
                                    </div>
                                    <div class="row mt-3">
                                        <div class="col-md-6">
                                            <h6>❌ Cancel Appointment</h6>
                                            <code>Cancel [DD-MM-YYYY] [HH:MM]</code>
                                            <p class="small text-muted mt-1">Example: Cancel 25-08-2025 14:30</p>
                                        </div>
                                        <div class="col-md-6">
                                            <h6>❓ Get Help</h6>
                                            <code>Help</code>
                                            <p class="small text-muted mt-1">Shows all available commands</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-4 text-center">
                        <p class="text-muted">
                            <small>Business Hours: 9:00 AM - 5:00 PM | Available Slots: Every 30 minutes</small>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

# Create database tables
with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    app.logger.info("Database tables created successfully")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
