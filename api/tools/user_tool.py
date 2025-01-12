import logging
import json
import os
from typing import Dict
from langchain.schema import Document

# Set up logging
logger = logging.getLogger(__name__)

class UserInfoTool:
    """Tool for fetching user booking information"""
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        # Load bookings from JSON file
        bookings_path = os.path.join(os.path.dirname(__file__), '../booking/bookings.json')
        try:
            with open(bookings_path, 'r') as f:
                self.bookings_db = json.load(f)
            logger.info(f"Successfully loaded {len(self.bookings_db)} bookings from {bookings_path}")
        except Exception as e:
            logger.error(f"Error loading bookings from {bookings_path}: {str(e)}")
            self.bookings_db = {}

    def get_user_info(self, booking_number: str) -> Dict:
        """Fetch user information from booking number"""
        try:
            if not booking_number:
                return {
                    "error": "Please provide a booking number. Format: BKxxx (e.g., BK001, BK002)",
                    "example": "Example booking numbers: BK001, BK002, BK003"
                }

            booking_info = self.bookings_db.get(booking_number)
            if not booking_info:
                available_bookings = ", ".join(sorted(self.bookings_db.keys())[:5])
                return {
                    "error": f"Booking number '{booking_number}' not found. Please check your booking number.",
                    "hint": f"Available booking numbers for testing: {available_bookings}...",
                    "format": "Booking numbers should be in format BKxxx (e.g., BK001)"
                }

            # Add user context to vector store
            user_context = f"""
            Guest Information:
            Name: {booking_info['guest_name']} (Age: {booking_info['guest_age']})
            Room: {booking_info['room_number']}
            Stay Period: {booking_info['check_in']} to {booking_info['check_out']}
            Room Type: {booking_info['preferences']['room_type']} (Capacity: {booking_info['preferences']['capacity']})
            Dietary Preferences: {booking_info['preferences']['dietary']}
            Special Requests: {', '.join(booking_info['preferences']['special_requests'])}
            Preferred Activities: {', '.join(booking_info['preferences']['preferred_activities'])}
            Children: {'Yes' if booking_info['preferences']['children'] else 'No'}
            """
            
            # Create a new document with user context
            user_doc = Document(page_content=user_context, metadata={"source": "user_info"})
            
            # Add to vector store
            self.vectorstore.add_documents([user_doc])
            
            return booking_info
            
        except Exception as e:
            logger.error(f"Error fetching user info: {str(e)}")
            return {
                "error": "Error fetching user information",
                "details": str(e),
                "hint": "Please try with a valid booking number (e.g., BK001)"
            }

    def format_user_info(self, booking_info: Dict) -> str:
        """Format user information for agent consumption"""
        if "error" in booking_info:
            error_message = f"Error: {booking_info['error']}"
            if "hint" in booking_info:
                error_message += f"\nHint: {booking_info['hint']}"
            if "format" in booking_info:
                error_message += f"\nFormat: {booking_info['format']}"
            if "example" in booking_info:
                error_message += f"\n{booking_info['example']}"
            return error_message
            
        return f"""
        Guest Information:
        - Name: {booking_info['guest_name']} (Age: {booking_info['guest_age']})
        - Room: {booking_info['room_number']}
        - Check-in: {booking_info['check_in']}
        - Check-out: {booking_info['check_out']}
        
        Room Details:
        - Type: {booking_info['preferences']['room_type']}
        - Capacity: {booking_info['preferences']['capacity']} people
        - Children: {'Yes' if booking_info['preferences']['children'] else 'No'}
        
        Preferences:
        - Dietary: {booking_info['preferences']['dietary']}
        - Special Requests: {', '.join(booking_info['preferences']['special_requests'])}
        - Preferred Activities: {', '.join(booking_info['preferences']['preferred_activities'])}
        """ 