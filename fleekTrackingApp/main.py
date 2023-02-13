from flask import Flask, render_template, request
import requests
import json

# Create a Flask application
app = Flask(__name__, template_folder='templates')


# Define the default route
@app.route('/')
def index():
    # Render the index.html template
    return render_template('index.html')


# Define route to update index.html with data
@app.route('/', methods=['POST'])
def track():
    # Get the tracking number from the form data
    tracking_number = request.form['tracking_number']

    # API URL to get tracking information
    url = "https://api.ship24.com/public/v1/trackers/track"

    # Data to send in the API request
    payload = {
        "trackingNumber": tracking_number
    }

    # API headers
    headers = {
        'Authorization': 'Bearer <API-KEY>',
        'Content-Type': 'application/json; charset=utf-8'
    }

    try:
        # Make the API request to retrieve courier names
        couriers_url = 'https://api.ship24.com/public/v1/couriers'
        couriers = requests.get(couriers_url, headers=headers)

        # Raise an exception if the API response is not successful
        couriers.raise_for_status()

        # Get the JSON data from the API response
        couriers_json = couriers.json()

        # Create an array consisting of all courier details
        couriers_array = couriers_json.get('data').get('couriers')

    except requests.exceptions.RequestException as e:
        # Render an error message on the same page if there is an exception
        return render_template('index.html', error_message='error')

    try:
        # Make the API request
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # Raise an exception if the API response is not successful
        response.raise_for_status()

        # Get the JSON data from the API response
        response_json = response.json()

        data = response_json.get('data')
        trackings = data.get('trackings')
        tracker = trackings[0]
        events = tracker.get('events')
        shipment = tracker.get('shipment')
        status = shipment.get('statusMilestone').strip() #Get status milestone

        # Define dictionary for all status codes
        final_status_dict = {
            "pending": 'The shipment doesn’t have events available yet or can’t be found.',
            "info_received": 'The shipment has been declared electronically and/or is in preparation by the shipper.',
            "in_transit": "The shipment has been accepted or picked up from the shipper and is on the way.",
            "out_for_delivery": 'The shipment is about to be delivered, usually the same day.',
            "failed_attempt": "A delivery attempt was made and failed.",
            "available_for_pickup": "The shipment is ready to be picked up by the receiver.",
            "delivered": "The shipment has been delivered.",
            "exception": "The shipment can’t be delivered due to issues that seems to be final."
        }

        # Fetch the corresponding message to the status
        final_status = final_status_dict[status]

        # Fetch information from all tracking events
        tracking_events = []
        for i in events:
            courierCode = i.get('courierCode').strip() # Fetch courier code
            for j in couriers_array:
                if courierCode == j['courierCode']:
                    courierName = j['courierName'].strip() # Fetch courier name
                    courierWebsite = j['website'].strip() # Fetch courier website

            tracking_events.append({
                "status": i.get('status'), # Add tracking event status
                "datetime": i.get('datetime'), # Add tracking event date and time
                "location": i.get('location'), # Add tracking event location
                "courierCode": i.get('courierCode'), # Add tracking event courier code
                "courierName": courierName, # Add tracking event courier name
                "courierWebsite": courierWebsite # Add tracking event courier website
            })

        # Return template to render
        return render_template('index.html', tracking_updates=tracking_events,
                               final_status=final_status)
    except requests.exceptions.RequestException as e:
        # Render an error message on the same page if there is an exception
        return render_template('index.html', error_message='error')


# Run the application if this script is run as the main program
if __name__ == '__main__':
    app.run(debug=True)
