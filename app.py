import uuid

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:admin@mysql/balance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Invoice(db.Model):
    __tablename__ = "invoice"

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100))
    balance = db.Column(db.Float, nullable=False)


@app.route('/create_invoice', methods=['POST'])
def create_invoice():
    name = request.json.get('name')
    invoice_id = str(uuid.uuid4())
    invoice = Invoice(id=invoice_id, name=name, balance=0.0)
    db.session.add(invoice)
    db.session.commit()
    return jsonify({"id": invoice_id, "name": name, "balance": 0.0}), 201


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    try:
        invoice_id = request.json.get('id')
        diff = request.json.get('diff')
        if not invoice_id or diff is None:
            return jsonify({"error": "Invalid input"}), 400

        invoice = Invoice.query.filter_by(id=invoice_id).first()
        if invoice is None:
            return jsonify({"error": "Invoice not found"}), 404

        invoice.balance += float(diff)
        db.session.commit()
        return jsonify({"message": "Transaction added successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/balance', methods=['GET'])
def balance():
    invoice_id = request.args.get('id')
    if not invoice_id:
        return jsonify({"error": "No ID provided"}), 400

    try:
        invoice = Invoice.query.filter_by(id=invoice_id).first()

        if invoice is None:
            return jsonify({"error": "Invoice not found"}), 404

        return jsonify({"balance": invoice.balance}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', port=7000)