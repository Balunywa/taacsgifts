from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from azure.notificationhubs import NotificationHubClient, NotificationHubError

params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=giftcricledbserver.database.windows.net;DATABASE=giftcricle;UID=balunlu;PWD=Luq#123450;Connection Timeout=60")

conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False

db = SQLAlchemy(app)

hub_connection_string = '<notification_hub_connection_string>'
hub_name = '<notification_hub_name>'
hub_client = NotificationHubClient(hub_connection_string, hub_name)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class Attendee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    email = db.Column(db.String(255), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events', methods=['GET', 'POST'])
def events():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        time = request.form['time']
        location = request.form['location']
        description = request.form['description']

        new_event = Event(name=name, date=date, time=time, location=location, description=description)
        db.session.add(new_event)
        db.session.commit()

    events = Event.query.all()

    return render_template('events.html', events=events)

@app.route('/checkin', methods=['POST'])
def checkin():
    data = request.get_json()
    event_id = data['event_id']
    user_id = data['user_id']
    latitude = data['latitude']
    longitude = data['longitude']

    event = Event.query.get(event_id)

    # Send check-in notification to all attendees
    message = event.name + ' has checked in.'
    tags = ['event-' + str(event_id)]
    try:
        hub_client.send_notification(message, tags)
        return jsonify({'message': 'Check-in successful'})
    except NotificationHubError as e:
        return jsonify({'message': 'Error sending notification: ' + str(e)})

@app.route('/invite', methods=['POST'])
def invite():
    data = request.get_json()
    event_id = data['event_id']
    email = data['email']

    new_attendee = Attendee(event_id=event_id, email=email)
    db.session.add(new_attendee)
    db.session.commit()

    # Send invitation push notification to the recipient
    message = 'You have been invited to an event.'
    tags = ['event-' + str(event_id), 'user-' + email]
    try:
        hub_client.send_notification(message, tags)
        return jsonify({'message': 'Invitation sent'})
    except NotificationHubError as e:
        return jsonify({'message': 'Error sending notification: ' + str(e)})

if __name__ == '__main__':
    db.create_all()
    app.run()
