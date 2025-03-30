from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
from event_data import (
    get_upcoming_events,
    get_past_events,
    get_event_by_id,
    get_events_by_category,
    get_registration_info,
    get_rewards,
    get_faq,
    get_categories
)

# Load environment variables from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Chat history to maintain context
chat_history = {}

def get_event_context():
    """Get formatted event data for context"""
    try:
        context = "Here is the current event information:\n\n"
        
        # Add upcoming events
        context += "UPCOMING EVENTS:\n"
        upcoming_events = get_upcoming_events()
        for event in upcoming_events:
            context += f"- {event['title']} ({event['date']})\n"
            context += f"  Price: {event['price']}\n"
            context += f"  Location: {event['location']}\n"
            context += f"  Category: {event['category']}\n"
            context += f"  Description: {event['description']}\n"
            context += f"  Available Spots: {event['capacity'] - event['registered']}\n\n"
        
        # Add categories
        context += "AVAILABLE CATEGORIES:\n"
        categories = get_categories()
        for category in categories:
            context += f"- {category}\n"
        
        # Add registration info
        reg_info = get_registration_info()
        context += "\nREGISTRATION PROCESS:\n"
        for step in reg_info['process']:
            context += f"- {step}\n"
        
        return context
    except Exception as e:
        print(f"Error getting event context: {str(e)}")
        return "Error retrieving event information."

def process_message(message):
    """Process user message using Gemini API with event context"""
    try:
        # Check for upcoming events query
        if any(keyword in message.lower() for keyword in ['upcoming', 'future', 'next', 'coming', 'events']):
            upcoming_events = get_upcoming_events()
            response = "🎉 Here are our upcoming events:\n\n"
            
            for event in upcoming_events:
                response += f"📅 {event['title']}\n"
                response += f"📅 Date: {event['date']}\n"
                response += f"⏰ Time: {event['time']}\n"
                response += f"📍 Location: {event['location']}\n"
                response += f"💰 Price: {event['price']}\n"
                response += f"📝 Description: {event['description']}\n"
                response += f"🎫 Available Spots: {event['capacity'] - event['registered']}\n"
                response += f"🏷️ Category: {event['category']}\n"
                
                # Add ticket types if available
                if 'ticket_types' in event:
                    response += "\n🎫 Ticket Types:\n"
                    for ticket in event['ticket_types']:
                        response += f"- {ticket['name']}: {ticket['price']}\n"
                
                response += "\n" + "="*50 + "\n\n"
            
            return response

        # Get event context for other queries
        event_context = get_event_context()
        
        # Create prompt with context and user message
        prompt = f"""You are an AI assistant for an event management system. Here is the current event information:

{event_context}

User message: {message}

Please provide a helpful response based on the event information. If the user is asking about specific events, registration, or categories, use the provided information. If the question is general, provide a helpful response about event management.

Response:"""
        
        # Generate response using Gemini
        response = model.generate_content(prompt)
        
        # Check if response is valid
        if response and response.text:
            return response.text
        else:
            return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
        
    except Exception as e:
        print(f"Error in Gemini API: {str(e)}")
        # Fallback response with event information
        try:
            upcoming_events = get_upcoming_events()
            response = "Here are our upcoming events:\n\n"
            for event in upcoming_events:
                response += f"📅 {event['title']}\n"
                response += f"Date: {event['date']}\n"
                response += f"Time: {event['time']}\n"
                response += f"Location: {event['location']}\n"
                response += f"Price: {event['price']}\n"
                response += f"Available Spots: {event['capacity'] - event['registered']}\n\n"
            return response
        except:
            return "I apologize, but I'm having trouble accessing the event information. Please try again later."

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400

        # Get or create chat history for the session
        session_id = request.headers.get('X-Session-ID', 'default')
        if session_id not in chat_history:
            chat_history[session_id] = []

        # Add user message to history
        chat_history[session_id].append({"role": "user", "content": message})

        # Process message and get response
        bot_response = process_message(message)

        # Add bot response to history
        chat_history[session_id].append({"role": "assistant", "content": bot_response})

        # Keep only last 10 messages to maintain context
        if len(chat_history[session_id]) > 10:
            chat_history[session_id] = chat_history[session_id][-10:]

        return jsonify({
            'response': bot_response,
            'status': 'success'
        })

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your request',
            'details': str(e)
        }), 500

@app.route('/clear', methods=['POST'])
def clear_chat():
    try:
        session_id = request.headers.get('X-Session-ID', 'default')
        if session_id in chat_history:
            chat_history[session_id] = []
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 