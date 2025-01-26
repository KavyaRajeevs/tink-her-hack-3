from flask import Flask, request, jsonify
import random
import string
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Predefined main user (username and password)
main_user = {
    "username": "main_user",
    "password": "mainpassword"
}

# Store sub-users data and their generated keys
sub_users = {}
pending_keys = {}

# Function to generate a unique key
def generate_key(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# Main User Login (Authentication)
@app.route('/main_user_login', methods=['POST'])
def main_user_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username == main_user["username"] and password == main_user["password"]:
        return jsonify({"message": "Main user login successful!"}), 200
    else:
        return jsonify({"message": "Invalid main user credentials!"}), 403


# Create Sub-User
@app.route('/create_sub_user', methods=['POST'])
def create_sub_user():
    data = request.json
    main_username = data.get("main_username")
    main_password = data.get("main_password")

    if main_username == main_user["username"] and main_password == main_user["password"]:
        sub_username = data.get("sub_username")
        sub_password = data.get("sub_password")
        
        # Check if sub-username already exists
        if sub_username in sub_users:
            return jsonify({"message": "Sub-user already exists!"}), 400
        
        # Create the sub-user and generate a key for login validation
        sub_key = generate_key()
        sub_users[sub_username] = {
            'sub_password': sub_password,
            'sub_key': sub_key,
        }

        # Store the key in pending keys (for the main user to approve it)
        pending_keys[sub_username] = sub_key

        # Send the key to the main user's page (simulating here by returning the key)
        return jsonify({
            "message": f"Sub-user {sub_username} created.",
            "sub_user_key": sub_key,
            "note": "The key has been sent to the main user for approval."
        }), 201
    else:
        return jsonify({"message": "Invalid main user credentials!"}), 403


# Main User Approves Sub-User Key (Sends key to sub-user)
@app.route('/approve_sub_user_key', methods=['POST'])
def approve_sub_user_key():
    data = request.json
    main_username = data.get("main_username")
    main_password = data.get("main_password")
    sub_username = data.get("sub_username")

    if main_username == main_user["username"] and main_password == main_user["password"]:
        if sub_username in sub_users and sub_username in pending_keys:
            key = pending_keys.pop(sub_username)  # Remove the key from pending keys
            return jsonify({"message": f"Key for sub-user {sub_username} approved. Key: {key}"}), 200
        else:
            return jsonify({"message": "Sub-user not found or key already approved."}), 400
    else:
        return jsonify({"message": "Invalid main user credentials!"}), 403


# Sub-User Login (Sub-user enters the key to log in)
@app.route('/sub_user_login', methods=['POST'])
def sub_user_login():
    data = request.json
    sub_username = data.get("sub_username")
    sub_password = data.get("sub_password")
    sub_key = data.get("sub_key")

    # Check if the sub-user exists and credentials match
    if sub_username in sub_users:
        if sub_users[sub_username]['sub_password'] == sub_password:
            # Validate the key
            if sub_users[sub_username]['sub_key'] == sub_key:
                return jsonify({"message": f"Sub-user {sub_username} login successful!"}), 200
            else:
                return jsonify({"message": "Invalid key! Login failed."}), 403
        else:
            return jsonify({"message": "Invalid sub-user password!"}), 403
    else:
        return jsonify({"message": "Sub-user does not exist!"}), 404
# Configure the database URI (SQLite in this case)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop_owner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the ShopOwner model to store shop details
class ShopOwner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_name = db.Column(db.String(100), nullable=False)
    upi_id = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<ShopOwner {self.shop_name}>'

# Route to register a shop owner
@app.route('/register', methods=['GET', 'POST'])
def register_shop():
    if request.method == 'POST':
        shop_name = request.form['shop_name']
        upi_id = request.form['upi_id']

        # Create a new ShopOwner object
        new_shop_owner = ShopOwner(shop_name=shop_name, upi_id=upi_id)

        # Add the new shop owner to the database
        db.session.add(new_shop_owner)
        db.session.commit()

        return redirect(url_for('view_shops'))

    return render_template('register_shop.html')

# Route to view the list of registered shops
@app.route('/shops')
def view_shops():
    shops = ShopOwner.query.all()
    return render_template('view_shops.html', shops=shops)



if __name__ == "__main__":
    app.run(debug=True)

