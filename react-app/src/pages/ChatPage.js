import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/ChatPage.css';

function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();
  const bookingNumber = sessionStorage.getItem('bookingNumber');

  useEffect(() => {
    if (!bookingNumber) {
      navigate('/');
      return;
    }
    // Add welcome message
    setMessages([
      {
        type: 'assistant',
        content: 'Hello! How can I assist you today?'
      }
    ]);
  }, [bookingNumber, navigate]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage,
          booking_number: bookingNumber
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessages(prev => [...prev, { type: 'assistant', content: data.response }]);
      } else {
        setMessages(prev => [...prev, { type: 'error', content: data.message }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { type: 'error', content: 'Failed to send message. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-container">
        <div className="chat-header">
          <h2>Guest Assistant</h2>
          <button onClick={() => navigate('/')} className="new-chat-button">
            New Chat
          </button>
        </div>

        <div className="messages-container">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.type}`}>
              {message.content}
            </div>
          ))}
          {isLoading && (
            <div className="message assistant loading">
              Thinking...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatPage; 