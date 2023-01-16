from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from lib.dilithium_cipher import DilithiumCipher
from lib.ecc_cipher import EccCipher
from lib.rsa_cipher import RsaCipher
from .transaction import ClientTransaction

# Initialize Flask app
app = Flask(__name__)
CORS(app)

CIPHER_TYPE = "ECC"

if CIPHER_TYPE == "ECC":
    cipher = EccCipher()
elif CIPHER_TYPE == "RSA":
    cipher = RsaCipher()
elif CIPHER_TYPE == "Dilithium":
    cipher = DilithiumCipher()
else:
    raise ValueError(CIPHER_TYPE + "is unknown")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/make/transaction")
def make_transaction():
    return render_template("make_transaction.html")


@app.route("/view/transactions")
def view_transaction():
    return render_template("view_transactions.html")


@app.route("/wallet/new", methods=["GET"])
def new_wallet():

    private_key, public_key = cipher.get_key_pair()
    response = {
        "private_key": private_key,
        "public_key": public_key,
    }
    return jsonify(response), 200


@app.route("/generate/transaction", methods=["POST"])
def generate_transaction():
    sender_address = request.form["sender_address"]
    sender_private_key = request.form["sender_private_key"]
    receiver_address = request.form["receiver_address"]
    amount = request.form["amount"]

    transaction = ClientTransaction(
        sender_address, sender_private_key, receiver_address, amount
    )

    response = {
        "transaction": transaction.to_dict(),
        "signature": cipher.sign(sender_private_key, str(transaction.to_dict())),
    }

    return jsonify(response), 200
