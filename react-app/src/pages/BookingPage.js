import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/BookingPage.css';

function BookingPage() {
  const [bookingNumber, setBookingNumber] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          booking_number: bookingNumber,
          query: "Hello" // Initial test query
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Store booking number in session storage
        sessionStorage.setItem('bookingNumber', bookingNumber);
        navigate('/chat');
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to connect to the server. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="booking-page">
      <div className="booking-container">
        <h1>Welcome to Guest Assistant</h1>
        <p>Please enter your booking number to continue</p>
        
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <input
              type="text"
              value={bookingNumber}
              onChange={(e) => setBookingNumber(e.target.value.toUpperCase())}
              placeholder="Enter booking number (e.g., BK001)"
              disabled={isLoading}
            />
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <button type="submit" disabled={isLoading || !bookingNumber}>
            {isLoading ? 'Verifying...' : 'Continue'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default BookingPage; 