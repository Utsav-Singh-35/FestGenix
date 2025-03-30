def get_upcoming_events():
    return [
        {
            'title': 'Tech Conference 2024',
            'date': '2024-04-15',
            'time': '10:00 AM',
            'location': 'Convention Center',
            'price': '₹24,999',
            'description': 'Annual technology conference featuring the latest innovations',
            'capacity': 500,
            'registered': 300,
            'category': 'Technology',
            'ticket_types': [
                {'name': 'Early Bird', 'price': '₹19,999'},
                {'name': 'Regular', 'price': '₹24,999'},
                {'name': 'VIP', 'price': '₹34,999'}
            ]
        },
        {
            'title': 'Startup Summit 2024',
            'date': '2024-05-01',
            'time': '9:00 AM',
            'location': 'Innovation Hub',
            'price': '₹31,999',
            'description': 'Connect with successful entrepreneurs and investors',
            'capacity': 300,
            'registered': 150,
            'category': 'Business',
            'ticket_types': [
                {'name': 'Standard', 'price': '₹31,999'},
                {'name': 'Premium', 'price': '₹41,999'}
            ]
        }
    ]

def get_past_events():
    return [
        {
            'title': 'AI Workshop 2023',
            'date': '2023-12-10',
            'category': 'Technology'
        }
    ]

def get_event_by_id(event_id):
    events = get_upcoming_events() + get_past_events()
    for event in events:
        if event.get('id') == event_id:
            return event
    return None

def get_events_by_category(category):
    events = get_upcoming_events() + get_past_events()
    return [event for event in events if event.get('category') == category]

def get_registration_info():
    return {
        'process': [
            'Select an event from the upcoming events list',
            'Choose your preferred ticket type',
            'Fill in your personal details',
            'Complete the payment process',
            'Receive confirmation email with event details'
        ]
    }

def get_rewards():
    return [
        {
            'name': 'Early Bird Discount',
            'points': 100,
            'description': '20% off on registration'
        },
        {
            'name': 'VIP Access',
            'points': 200,
            'description': 'Exclusive speaker access and networking events'
        }
    ]

def get_faq():
    return [
        {
            'question': 'How do I register for an event?',
            'answer': 'Select an event, choose your ticket type, fill in details, and complete payment.'
        },
        {
            'question': 'What\'s the cancellation policy?',
            'answer': 'Free cancellation up to 7 days before the event.'
        }
    ]

def get_categories():
    return ['Technology', 'Business', 'Education', 'Entertainment', 'Sports'] 