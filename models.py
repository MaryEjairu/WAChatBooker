from app import db
from datetime import datetime

class Appointment(db.Model):
    """
    Model for storing appointment bookings
    """
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)  # WhatsApp number
    date = db.Column(db.String(10), nullable=False)  # Format: DD-MM-YYYY
    time = db.Column(db.String(5), nullable=False)   # Format: HH:MM
    status = db.Column(db.String(20), nullable=False, default='confirmed')  # confirmed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Appointment {self.name} on {self.date} at {self.time}>'
    
    def to_dict(self):
        """
        Convert appointment to dictionary for easy handling
        """
        return {
            'id': self.id,
            'name': self.name,
            'phone_number': self.phone_number,
            'date': self.date,
            'time': self.time,
            'status': self.status,
            'created_at': self.created_at
        }
    
    @staticmethod
    def is_slot_available(date, time, exclude_id=None):
        """
        Check if a specific date/time slot is available
        """
        query = Appointment.query.filter_by(
            date=date, 
            time=time, 
            status='confirmed'
        )
        
        # Exclude specific appointment ID (useful for updates)
        if exclude_id:
            query = query.filter(Appointment.id != exclude_id)
            
        return query.first() is None
    
    @staticmethod
    def get_user_appointments(phone_number):
        """
        Get all confirmed appointments for a specific phone number
        """
        return Appointment.query.filter_by(
            phone_number=phone_number,
            status='confirmed'
        ).order_by(Appointment.date, Appointment.time).all()
    
    @staticmethod
    def find_next_available_slot(preferred_date, preferred_time):
        """
        Find the next available appointment slot after the preferred time
        This is a simple implementation - in a real app, you'd have business hours logic
        """
        from date_utils import get_next_time_slot, is_valid_date_time
        
        # Start checking from the preferred time
        current_date = preferred_date
        current_time = preferred_time
        
        # Check next 7 days, 8 hours per day (9 AM to 5 PM)
        for day_offset in range(7):
            for hour in range(9, 17):  # 9 AM to 4 PM (last slot)
                check_time = f"{hour:02d}:00"
                
                if Appointment.is_slot_available(current_date, check_time):
                    return current_date, check_time
            
            # Move to next day
            current_date = get_next_time_slot(current_date, "00:00")[0]
        
        return None, None  # No slots available in next 7 days
