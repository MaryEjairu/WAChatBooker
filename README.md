# WhatsApp Appointment Booking Bot

## Overview

A complete WhatsApp appointment booking bot built with Flask and Twilio's WhatsApp API. Users can book, view, and cancel appointments through natural language WhatsApp messages. The bot validates appointment times, checks availability, and manages data through a SQLite database.

## Features

### 🗓️ Appointment Booking
- Book appointments with natural language messages
- Validates date and time formats (DD-MM-YYYY HH:MM)
- Checks business hours (9 AM - 5 PM)
- Only allows 30-minute intervals (9:00, 9:30, 10:00, etc.)
- Confirms availability before booking

### 📱 User-Friendly Commands
- **Book:** "Book John Doe 15-08-2025 14:30"
- **View:** "My appointments" 
- **Cancel:** "Cancel 15-08-2025 14:30"
- **Help:** "Help" or "Menu"

### ✅ Smart Features
- Suggests next available slot if requested time is taken
- Friendly, professional responses with emojis
- Input validation and error handling
- Future date/time validation (at least 1 hour ahead)

## Quick Start

### Prerequisites
- Python 3.11+
- Twilio account with WhatsApp sandbox setup
- Replit environment (recommended)


### 🚀 Automated Setup 

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MaryEjairu/WAChatBooker.git
   cd WAChatBooker
   ```



2. **Configure environment variables**:
   ```bash
   cp .env.template .env
   # Edit .env file with your Twilio credentials
   ```

3. **Run automated setup**:
   ```bash
   python setup.py
   ```

4. **Start the application**:
   ```bash
   python main.py
   ```

   ### 📱 Twilio Setup

1. **Create Twilio Account**: Visit [twilio.com](https://twilio.com) and sign up
2. **WhatsApp Sandbox**: Go to Console → Messaging → Try it out → Send a WhatsApp message
3. **Get Credentials**: Copy your Account SID, Auth Token, and WhatsApp phone number
4. **Configure Webhook**: 
   - URL: `https://your-domain.com/webhook`
   - Method: POST
   - Save configuration

## Usage Examples

### Booking an Appointment
```
User: Book Mary Johnson 20-08-2025 10:30
Bot: Hello Mary Johnson, your appointment for 20 August 2025 at 10:30 AM is confirmed! ✅

Appointment Details:
👤 Name: Mary Johnson
📅 Date: 20 August 2025
🕐 Time: 10:30 AM
📱 Phone: whatsapp:+1234567890

We look forward to seeing you! If you need to cancel or reschedule, just let me know.
```

### Viewing Appointments
```
User: My appointments
Bot: Your upcoming appointments: 📅

👤 Mary Johnson
📅 20 August 2025
🕐 10:30 AM
📋 Status: Confirmed
─────────────────
To cancel an appointment, send:
Cancel [DD-MM-YYYY] [HH:MM]
```

### Canceling an Appointment
```
User: Cancel 20-08-2025 10:30
Bot: Your appointment has been cancelled successfully! ✅

Cancelled Appointment:
👤 Name: Mary Johnson
📅 Date: 20 August 2025
🕐 Time: 10:30 AM

The slot is now available for other bookings. Thank you!
```

## API Endpoints

### POST /webhook
Receives incoming WhatsApp messages from Twilio and processes them.

**Request Body:** Twilio webhook format
**Response:** TwiML MessagingResponse

### GET /health
Health check endpoint to verify the application is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "WhatsApp Appointment Bot is running"
}
```

## Project Structure

```
├── app.py                      # Flask application setup and webhook endpoint
├── bot_handler.py              # Main message processing logic  
├── models.py                   # SQLAlchemy database models
├── date_utils.py               # Date/time validation and formatting utilities
├── main.py                     # Application entry point
├── setup.py                    # Automated setup script
├── requirements.txt   # Python dependencies 
├── .env.template               # Environment variables template
├── .gitignore                  # Git ignore file
├── pyproject.toml              # Python project configuration
├── replit.md                   # Technical architecture documentation
└── README.md                   # This documentation
```


## Database Schema

### Appointments Table
- `id` (Integer, Primary Key)
- `name` (String, 100 chars)
- `phone_number` (String, 20 chars) - WhatsApp number
- `date` (String, 10 chars) - Format: DD-MM-YYYY
- `time` (String, 5 chars) - Format: HH:MM
- `status` (String, 20 chars) - 'confirmed' or 'cancelled'
- `created_at` (DateTime) - Auto-generated timestamp

## Business Rules

### Operating Hours
- **Business Hours:** 9:00 AM - 5:00 PM
- **Available Slots:** Every 30 minutes (9:00, 9:30, 10:00, etc.)
- **Advance Booking:** Minimum 1 hour in advance
- **Date Format:** DD-MM-YYYY (e.g., 15-08-2025)
- **Time Format:** HH:MM in 24-hour format (e.g., 14:30)

### Validation Rules
- Appointments must be in the future (at least 1 hour ahead)
- Only business hours are accepted
- Only 30-minute intervals are allowed
- Duplicate slots are prevented
- Phone number tracking for user-specific operations

## Error Handling

The bot handles various error scenarios gracefully:
- Invalid date/time formats
- Past dates/times
- Outside business hours
- Duplicate bookings
- Missing appointment details
- Database errors
- Twilio API errors

## Testing

### Manual Testing
Send these messages to your WhatsApp bot:

1. **Valid booking:** "Book John Doe 25-08-2025 14:30"
2. **Invalid format:** "Book John tomorrow 3pm"
3. **Past date:** "Book John 01-01-2020 10:00"
4. **View appointments:** "My appointments"
5. **Cancel:** "Cancel 25-08-2025 14:30"
6. **Help:** "Help"

### Webhook Testing
You can test the webhook endpoint directly:
```bash
curl -X POST http://localhost:5000/webhook \
  -d "Body=Book John Doe 25-08-2025 14:30" \
  -d "From=whatsapp:+1234567890"
```

## Troubleshooting

### Common Issues

1. **Bot not responding:**
   - Check Twilio webhook URL is correct
   - Verify environment variables are set
   - Check application logs for errors

2. **Database errors:**
   - Ensure SQLite database is writable
   - Check for proper table creation

3. **Date/time validation errors:**
   - Verify format is DD-MM-YYYY HH:MM
   - Ensure time is within business hours
   - Check that date is in the future

### Logs
The application includes comprehensive logging. Check the console output for:
- Incoming message details
- Processing steps
- Error messages
- Database operations


### Production Considerations
- Use PostgreSQL instead of SQLite for production
- Implement rate limiting
- Add authentication for admin endpoints
- Set up monitoring and alerting
- Use proper logging infrastructure
- Consider horizontal scaling for high traffic

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License
This project is open source and available under the MIT License. Built with ❤️ by Mary Ejairu
