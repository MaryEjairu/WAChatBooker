import re
import os
from app import db
from models import Appointment
from date_utils import (
    is_valid_date_time, 
    format_date_for_display, 
    format_time_for_display,
    parse_cancel_message
)
from twilio.rest import Client

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

def send_twilio_message(to_phone_number: str, message: str) -> None:
    """
    Send a message via Twilio WhatsApp API
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        
        print(f"Message sent with SID: {message.sid}")
    except Exception as e:
        print(f"Error sending message: {str(e)}")

def extract_booking_details(message):
    """
    Extract name, date, and time from booking message
    Expected formats:
    - "Book John Doe 15-08-2025 14:30"
    - "I want to book an appointment for John Doe on 15-08-2025 at 14:30"
    - "My name is John Doe, I need appointment on 15-08-2025 at 14:30"
    """
    message = message.strip()
    
    # Pattern 1: "Book [Name] [Date] [Time]"
    pattern1 = r'book\s+(.+?)\s+(\d{2}-\d{2}-\d{4})\s+(\d{1,2}:\d{2})'
    match = re.search(pattern1, message, re.IGNORECASE)
    
    if match:
        name = match.group(1).strip()
        date = match.group(2)
        time = match.group(3)
        
        # Ensure time is in HH:MM format
        if len(time.split(':')[0]) == 1:
            hour, minute = time.split(':')
            time = f"{hour.zfill(2)}:{minute}"
        
        return name, date, time
    
    # Pattern 2: Look for date and time patterns anywhere in the message
    date_pattern = r'(\d{2}-\d{2}-\d{4})'
    time_pattern = r'(\d{1,2}:\d{2})'
    
    date_match = re.search(date_pattern, message)
    time_match = re.search(time_pattern, message)
    
    if date_match and time_match:
        date = date_match.group(1)
        time = time_match.group(1)
        
        # Ensure time is in HH:MM format
        if len(time.split(':')[0]) == 1:
            hour, minute = time.split(':')
            time = f"{hour.zfill(2)}:{minute}"
        
        # Extract name (everything before the date, excluding common words)
        message_before_date = message[:date_match.start()].strip()
        
        # Remove common booking words and extract name
        name_text = re.sub(r'\b(book|appointment|for|my name is|i am|i\'m|want to|need|on|at)\b', '', message_before_date, flags=re.IGNORECASE)
        name = re.sub(r'\s+', ' ', name_text).strip()
        
        if name and len(name) > 1:
            return name, date, time
    
    return None, None, None

def handle_appointment_booking(message, phone_number):
    """
    Handle appointment booking requests
    """
    name, date, time = extract_booking_details(message)
    
    if not name or not date or not time:
        return """I'd be happy to help you book an appointment! 📅

Please provide your booking details in this format:
Book [Your Name] [DD-MM-YYYY] [HH:MM]

Example: Book John Doe 15-08-2025 14:30

Business hours: 9:00 AM - 5:00 PM
Available slots: Every 30 minutes (9:00, 9:30, 10:00, etc.)"""
    
    # Validate date and time
    if not is_valid_date_time(date, time):
        return f"""Sorry {name}, the date/time you provided is not valid. ❌

Please ensure:
• Date format: DD-MM-YYYY (e.g., 15-08-2025)
• Time format: HH:MM in 24-hour format (e.g., 14:30)
• Appointment must be at least 1 hour in the future
• Business hours: 9:00 AM - 5:00 PM
• Available slots: Every 30 minutes only (9:00, 9:30, 10:00, etc.)

Please try again with a valid date and time."""
    
    # Check if slot is available
    if not Appointment.is_slot_available(date, time):
        # Find next available slot
        next_date, next_time = Appointment.find_next_available_slot(date, time)
        
        if next_date and next_time:
            next_date_display = format_date_for_display(next_date)
            next_time_display = format_time_for_display(next_time)
            
            return f"""Sorry {name}, the slot on {format_date_for_display(date)} at {format_time_for_display(time)} is already booked. ❌

The next available slot is:
📅 {next_date_display} at {next_time_display}

Would you like to book this slot instead? If yes, please send:
Book {name} {next_date} {next_time}"""
        else:
            return f"""Sorry {name}, the slot on {format_date_for_display(date)} at {format_time_for_display(time)} is not available, and I couldn't find any available slots in the next 7 days. ❌

Please try booking for a later date or contact us directly."""
    
    # Create the appointment
    try:
        appointment = Appointment(
            name=name,
            phone_number=phone_number,
            date=date,
            time=time,
            status='confirmed'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        date_display = format_date_for_display(date)
        time_display = format_time_for_display(time)
        
        return f"""Hello {name}, your appointment for {date_display} at {time_display} is confirmed! ✅

Appointment Details:
👤 Name: {name}
📅 Date: {date_display}
🕐 Time: {time_display}
📱 Phone: {phone_number}

We look forward to seeing you! If you need to cancel or reschedule, just let me know."""
        
    except Exception as e:
        return f"Sorry {name}, there was an error booking your appointment. Please try again later."

def handle_view_appointments(phone_number):
    """
    Handle requests to view appointments
    """
    appointments = Appointment.get_user_appointments(phone_number)
    
    if not appointments:
        return """You don't have any upcoming appointments. 📅

To book a new appointment, send:
Book [Your Name] [DD-MM-YYYY] [HH:MM]

Example: Book John Doe 15-08-2025 14:30"""
    
    response = "Your upcoming appointments: 📅\n\n"
    
    for apt in appointments:
        date_display = format_date_for_display(apt.date)
        time_display = format_time_for_display(apt.time)
        
        response += f"👤 {apt.name}\n"
        response += f"📅 {date_display}\n"
        response += f"🕐 {time_display}\n"
        response += f"📋 Status: {apt.status.title()}\n"
        response += "─────────────────\n"
    
    response += "\nTo cancel an appointment, send:\nCancel [DD-MM-YYYY] [HH:MM]"
    
    return response

def handle_cancel_appointment(message, phone_number):
    """
    Handle appointment cancellation requests
    """
    date, time = parse_cancel_message(message)
    
    if not date or not time:
        return """To cancel an appointment, please use this format:
Cancel [DD-MM-YYYY] [HH:MM]

Example: Cancel 15-08-2025 14:30

To see your appointments, type "My appointments" """
    
    # Find the appointment
    appointment = Appointment.query.filter_by(
        phone_number=phone_number,
        date=date,
        time=time,
        status='confirmed'
    ).first()
    
    if not appointment:
        date_display = format_date_for_display(date)
        time_display = format_time_for_display(time)
        
        return f"""No confirmed appointment found for {date_display} at {time_display}. ❌

To see your appointments, type "My appointments" """
    
    try:
        # Cancel the appointment
        appointment.status = 'cancelled'
        db.session.commit()
        
        date_display = format_date_for_display(date)
        time_display = format_time_for_display(time)
        
        return f"""Your appointment has been cancelled successfully! ✅

Cancelled Appointment:
👤 Name: {appointment.name}
📅 Date: {date_display}
🕐 Time: {time_display}

The slot is now available for other bookings. Thank you!"""
        
    except Exception as e:
        return "Sorry, there was an error cancelling your appointment. Please try again later."

def handle_whatsapp_message(message, phone_number):
    """
    Main message handler for WhatsApp bot
    """
    message = message.strip()
    message_lower = message.lower()
    
    # Handle different types of messages
    if message_lower in ['my appointments', 'appointments', 'my bookings', 'view appointments']:
        return handle_view_appointments(phone_number)
    
    elif message_lower.startswith('cancel'):
        return handle_cancel_appointment(message, phone_number)
    
    elif 'book' in message_lower or any(keyword in message_lower for keyword in ['appointment', 'schedule', 'meeting']):
        return handle_appointment_booking(message, phone_number)
    
    elif message_lower in ['help', 'menu', 'commands']:
        return """Welcome to our Appointment Booking Bot! 👋

Available commands:

📅 **Book an appointment:**
Book [Your Name] [DD-MM-YYYY] [HH:MM]
Example: Book John Doe 15-08-2025 14:30

📋 **View your appointments:**
Type "My appointments"

❌ **Cancel an appointment:**
Cancel [DD-MM-YYYY] [HH:MM]
Example: Cancel 15-08-2025 14:30

ℹ️ **Business hours:** 9:00 AM - 5:00 PM
**Available slots:** Every 30 minutes

Need help? Just type "help" anytime!"""
    
    else:
        # Default response for unrecognized messages
        return """Hi there! 👋 I'm your appointment booking assistant.

To book an appointment, send:
Book [Your Name] [DD-MM-YYYY] [HH:MM]

Example: Book John Doe 15-08-2025 14:30

Other commands:
• "My appointments" - View your bookings
• "Cancel [date] [time]" - Cancel a booking
• "Help" - See all commands

How can I help you today?"""
