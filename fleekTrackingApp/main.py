from flask import Flask, render_template, request
import requests
import json
import sys

# Create a Flask application
app = Flask(__name__, template_folder='templates')


# Define the default route
@app.route('/')
def index():
    # Render the index.html template
    #print('Hello world!', file=sys.stderr)
    return render_template('index.html')
    #return "Hello World!"

# Define the track route
@app.route('/', methods=['POST'])
def track():
    print('Hello world!', file=sys.stderr)
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
        'Authorization': 'Bearer apik_1vLgnO8wT7t8O5dvvR8qDhFthGArkm',
        'Content-Type': 'application/json; charset=utf-8'
    }

    try:
        couriers_url = 'https://api.ship24.com/public/v1/couriers'
        couriers = requests.get(couriers_url, headers=headers)

        couriers.raise_for_status()

        couriers_json = couriers.json()
        couriers_array = couriers_json.get('data').get('couriers')

    except requests.exceptions.RequestException as e:
        # Return an error message if an exception was raised
        return render_template('index.html', error_message = 'error')


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
        status = shipment.get('statusMilestone').strip()

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

        final_status = final_status_dict[status]

        tracking_events = []
        for i in events:
            courierCode = i.get('courierCode').strip()
            for j in couriers_array:
                if courierCode == j['courierCode']:
                    courierName= j['courierName'].strip()
                    courierWebsite = j['website'].strip()
                    print(courierWebsite)

            tracking_events.append({
                "status": i.get('status'),
                "datetime": i.get('datetime'),
                "location": i.get('location'),
                "courierCode": i.get('courierCode'),
                "courierName": courierName,
                "courierWebsite": courierWebsite
            })

        # Get the carrier detected by the API
        #carrier_detected = response_json.get('courierName', 'Unknown')

        # Get the tracking updates for the tracking number
        #tracking_updates = response_json.get('track', [])

        # Get the final status of delivered if the item is indeed delivered
        #final_status = 'Delivered' if response_json.get('deliveryStatus') == 'Delivered' else 'Not delivered'

        # Render the track.html template with the tracking information
        return render_template('index.html', tracking_updates=tracking_events,
                               final_status=final_status)
    except requests.exceptions.RequestException as e:
        # Return an error message if an exception was raised
        return render_template('index.html', error_message = 'error')


# Run the application if this script is run as the main program
if __name__ == '__main__':
    app.run(debug=True)

