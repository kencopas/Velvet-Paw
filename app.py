import stripe
from flask import Flask, request, render_template, abort, jsonify
from twilio.rest import Client
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText

from utils.logging import gotenv
from data_client import DataClient
from constants import INDEX_VARS

load_dotenv()
stripe.api_key = gotenv("REAL_STRIPE_SECRET_KEY")
app = Flask(__name__)
_dc = None
_cart = None


# Function for retreiving the DataClient
def get_dc() -> DataClient:
    global _dc
    if not _dc:
        _dc = DataClient()
    return _dc


def get_cart() -> dict:
    global _cart
    if not _cart:
        _cart = dict()
    return _cart


def send_twilio(body: str, to: str) -> str:
    """
    Send an SMS message with twilio.
    """
    account_sid = gotenv('TWILIO_ACCOUNT_SID')
    auth_token = gotenv('TWILIO_AUTH_TOKEN')
    phone_num = gotenv('TWILIO_PHONE_NUMBER')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=body,
        from_=phone_num,
        to=to
    )

    return message.sid


def send_sms(phone_number, message):
    """
    Send an SMS message with smtp gmail.
    """
    gmail_user = gotenv('SMTP_GMAIL')
    app_pass = gotenv('SMTP_APP_PASS')

    to_number = f"{phone_number}@tmomail.net"

    if not gmail_user or not app_pass:
        print('environment variables unset')
        print(gmail_user, app_pass)
        return

    msg = MIMEText(str(message))
    msg['From'] = gmail_user
    msg['To'] = to_number
    msg['Subject'] = ' '

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, app_pass)
        server.sendmail(gmail_user, to_number, msg.as_string())
        server.quit()
        print("SMS sent successfully!")
    except Exception as e:
        print("Failed to send SMS:", e)


def send_email(name, email, message):
    msg = EmailMessage()
    msg['Subject'] = f'New Contact Form Submission from {name}'
    msg['From'] = gotenv("EMAIL_USER")      # Your email address
    msg['To'] = gotenv("EMAIL_RECEIVER")    # Your inbox

    msg.set_content(f"From: {name}\nEmail: {email}\n\nMessage:\n{message}")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(gotenv("EMAIL_USER"), gotenv("EMAIL_PASS"))
        smtp.send_message(msg)


@app.route('/contact', methods=['POST'])
def contact():

    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    try:
        send_email(name, email, message)
        return render_template('index.html', show_modal=True, modal_type='success')
    except Exception as e:
        print(e)
        return render_template('index.html', show_modal=True, modal_type='error')


@app.before_request
def log_ip():
    print(f"Request from IP: {request.remote_addr} to {request.path}")


@app.route('/about')
def about():
    return render_template('about.html')


@app.route("/view-database")
def private_endpoint():
    """
    View the database information
    """
    # Retrieve the environment variables
    private_token = gotenv('PRIVATE_API_TOKEN')
    database = gotenv('MYSQL_DATABASE')
    table = gotenv('MYSQL_TABLE')

    # Retrieve the token from the url
    token = request.args.get("token")

    # Check if the token matches the private api token env variable
    if token != private_token:
        abort(403)

    # Retrieve the DataClient, select the database, and select all rows
    dc = get_dc()
    dc.sql.run(f'USE {database};')
    output = dc.sql.run(f'SELECT * FROM {table};')

    # If the table is not empty, pass data to view-database.html template
    if output:
        columns = output[0]
        rows = output[1:]
        return render_template(
            "view-database.html",
            rows=rows,
            columns=columns
        )
    else:
        return f"Empty table {table}"


@app.route('/menu')
def menu():
    return render_template('menu.html')


@app.route('/add_item', methods=['POST'])
def add_item():

    try:

        # Retrieve the cart and added item
        cart = get_cart()
        data = request.get_json()
        item, price = data['item'], data['price']

        print(f"Cart: {cart}\n\nItem: {item}")

        # Add or update the item
        if cart.get(item):
            cart[item]['qty'] += 1
        else:
            cart[item] = { 
                'price': price,
                'qty': 1
            }

        return jsonify({'message': 'Item added to cart.', 'cart': cart}), 200

    except Exception as err:
        return jsonify({'message': err})


@app.route('/cancel')
@app.route('/checkout', methods=['GET'])
def checkout():
    return render_template('checkout.html', stripe_public_key=gotenv("REAL_STRIPE_PUBLIC_KEY"))


@app.route('/success')
def success():
    return render_template('order-placed.html')


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        cart = request.get_json()
        print(cart)

        item_entries = [
            (item, info['price'], info['qty'])
            for item, info in cart.items()
        ]

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(price*100),  # $50.00
                    'product_data': {
                        'name': item,
                    },
                },
                'quantity': qty,
            } for item, price, qty in item_entries],
            mode='payment',
            success_url='https://velvetpawbakery.com/success',
            cancel_url='https://velvetpawbakery.com/cancel',
        )
        return jsonify({'id': session.id})
    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500


@app.route("/thank-you")
def thank_you():
    return render_template('thank-you.html')


# Render index.html at the root url
@app.route("/")
def home():
    # Retrieve all specified environment variables and pass to index.html
    index_kwargs = {key: gotenv(key.upper()) for key in INDEX_VARS}
    return render_template("index.html", **index_kwargs)


# Example submission endpoint
@app.route("/submit", methods=['POST'])
def submit():
    """
    Submission Endpoint

    Takes information optionally, passes to DataClient, renders a template
    """

    if request.form:

        info = request.form.to_dict()

        # Print and save the user info
        print(info)
        get_dc().handle_submit(info)

    return render_template("submitted.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
