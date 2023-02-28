import urllib.parse
import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=giftcricledbserver.database.windows.net;DATABASE=giftcricle;UID=balunlu;PWD=Luq#123450;Connection Timeout=60")

conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False

db = SQLAlchemy(app)

class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    msisdn = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<Contribution {self.name}: {self.amount}>'

# create the database tables before the first request is processed
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=['POST'])
def contribute():
    data = request.form
    name = data['name']
    msisdn = data['msisdn']
    amount = data['amount']

    # Save the contribution to the database
    contribution = Contribution(name=name, msisdn=msisdn, amount=amount)
    db.session.add(contribution)
    db.session.commit()

    # Make a request to the MTN MoMo API to initiate a collection request
    url = 'https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay'
    headers = {
        'X-Reference-Id': str(contribution.id),
        'Ocp-Apim-Subscription-Key': app.config['MTN_MOMO_COLLECTION_API_KEY'],
        'Authorization': f'Basic {app.config["MTN_MOMO_COLLECTION_API_USER"]}:{app.config["MTN_MOMO_COLLECTION_API_SECRET"]}',
        'Content-Type': 'application/json',
    }
    payload = {
        'amount': str(amount),
        'currency': 'UGX',
        'externalId': str(contribution.id),
        'payer': {
            'partyIdType': 'MSISDN',
            'partyId': msisdn
        },
        'payerMessage': f'Thank you for contributing {amount:.2f} UGX to Mr X.',
        'payeeNote': f'Thank you for contributing {amount:.2f} UGX to Mr X.'
    }
    response = requests.post(url, headers=headers, json=payload)

    return "Contribution saved and payment requested."

@app.route('/', methods=['GET'])
def contributions():
    # Retrieve all the contributions from the database
    contributions = Contribution.query.all()

    # Display the contributions in an HTML table
    table = '<table><thead><tr><th>Name</th><th>Amount</th><th>Transaction ID</th></tr></thead><tbody>'
    for contribution in contributions:
        table += f'<tr><td>{contribution.name}</td><td>{contribution.amount:.2f}</td><td>{contribution.transaction_id or "-"}</td></tr>'
    table += '</tbody></table>'

    return render_template('index.html', table=table)

if __name__ == '__main__':
   app.run(debug=True)

#if __name__ == '__main__':
 #  app.run()
