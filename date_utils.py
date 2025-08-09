import re
from datetime import datetime, timedelta

def is_valid_date_format(date_str):
    """
    Validate date format DD-MM-YYYY
    """
    pattern = r'^(\d{2})-(\d{2})-(\d{4})$'
    match = re.match(pattern, date_str)
    
    if not match:
        return False
    
    day, month, year = map(int, match.groups())
    
    try:
        # Check if the date is valid
        date_obj = datetime(year, month, day)
        
        # Check if the date is not in the past
        today = datetime.now().date()
        if date_obj.date() < today:
            return False
            
        return True
    except ValueError:
        return False

def is_valid_time_format(time_str):
    """
    Validate time format HH:MM (24-hour format)
    """
    pattern = r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$'
    match = re.match(pattern, time_str)
    
    if not match:
        return False
    
    hour, minute = map(int, match.groups())
    
    # Check business hours (9 AM to 5 PM)
    if hour < 9 or hour >= 17:
        return False
    
    # Only allow appointments on the hour or half-hour
    if minute not in [0, 30]:
        return False
        
    return True

def is_valid_date_time(date_str, time_str):
    """
    Validate both date and time, and check if it's not in the past
    """
    if not is_valid_date_format(date_str) or not is_valid_time_format(time_str):
        return False
    
    # Parse the date and time
    day, month, year = map(int, date_str.split('-'))
    hour, minute = map(int, time_str.split(':'))
    
    try:
        appointment_datetime = datetime(year, month, day, hour, minute)
        current_datetime = datetime.now()
        
        # Check if appointment is at least 1 hour in the future
        if appointment_datetime <= current_datetime + timedelta(hours=1):
            return False
            
        return True
    except ValueError:
        return False

def format_date_for_display(date_str):
    """
    Convert DD-MM-YYYY to a more readable format
    """
    try:
        day, month, year = date_str.split('-')
        date_obj = datetime(int(year), int(month), int(day))
        return date_obj.strftime('%d %B %Y')
    except:
        return date_str

def format_time_for_display(time_str):
    """
    Convert HH:MM to 12-hour format
    """
    try:
        hour, minute = map(int, time_str.split(':'))
        time_obj = datetime.strptime(f"{hour}:{minute}", "%H:%M")
        return time_obj.strftime('%I:%M %p')
    except:
        return time_str

def get_next_time_slot(date_str, time_str):
    """
    Get the next available time slot (30 minutes later)
    """
    try:
        day, month, year = map(int, date_str.split('-'))
        hour, minute = map(int, time_str.split(':'))
        
        current_time = datetime(year, month, day, hour, minute)
        next_time = current_time + timedelta(minutes=30)
        
        # If we go past business hours, move to next day at 9 AM
        if next_time.hour >= 17:
            next_day = next_time + timedelta(days=1)
            next_time = next_day.replace(hour=9, minute=0)
        
        next_date = next_time.strftime('%d-%m-%Y')
        next_time_str = next_time.strftime('%H:%M')
        
        return next_date, next_time_str
    except:
        return date_str, time_str

def parse_cancel_message(message):
    """
    Parse cancel message to extract date and time
    Expected format: "Cancel DD-MM-YYYY HH:MM" or "Cancel DD-MM-YYYY at HH:MM"
    """
    # Remove "cancel" and normalize the message
    message = re.sub(r'^cancel\s+', '', message.lower().strip())
    
    # Try different patterns
    patterns = [
        r'(\d{2}-\d{2}-\d{4})\s+(\d{1,2}:\d{2})',  # DD-MM-YYYY HH:MM
        r'(\d{2}-\d{2}-\d{4})\s+at\s+(\d{1,2}:\d{2})',  # DD-MM-YYYY at HH:MM
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            
            # Ensure time is in HH:MM format
            if len(time_str.split(':')[0]) == 1:
                hour, minute = time_str.split(':')
                time_str = f"{hour.zfill(2)}:{minute}"
            
            return date_str, time_str
    
    return None, None
