from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

politician = Blueprint("politician", __name__)


@politician.route("/fetchall/<int:user_id>", methods=["GET"])
def fetch_all(user_id):
    conn = db.get_db()
    cursor = conn.cursor()

    query = "SELECT politician_id, Name FROM Politicians WHERE user_id = " + \
        str(user_id)
    cursor.execute(query)
    allnames = cursor.fetchall()
    return jsonify(allnames), 200


@politician.route("/getID/<polName>", methods=["GET"])
def get_id(polName):
    conn = db.get_db()
    cursor = conn.cursor()

    query = "SELECT politician_id FROM Politicians WHERE name = %s"
    params = [polName]
    cursor.execute(query, params)
    id = cursor.fetchall()
    conn.commit()
    cursor.close()

    return jsonify(id), 200


@politician.route("/newPolitician", methods=["POST"])
def new_politician():
    conn = db.get_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO Politicians (name, contact_info, user_id)
    VALUES
    (%s, %s, %s)
    """
    params = []

    req = request.get_json()
    required_fields = ["name", "contact", "user_id"]
    for field in required_fields:
        if field not in req:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    for field in required_fields:
        params.append(req[field])
    cursor.execute(query, params)

    polId = cursor.lastrowid
    conn.commit()
    cursor.close()
    return jsonify({"message": "Note created successfully", "polID": polId}, 201)


@politician.route("/savePolicy", methods=["POST"])
def savePolicy():
    conn = db.get_db()
    cursor = conn.cursor()
    data = request.get_json()

    query = """
            INSERT INTO SavedPolicy 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    params = []

    required_fields = ["discountRate", "FederalReserveBalanceSheet",
              "TreasurySecurities", "HealthSpending", "MillitarySpending",
              "EducationSpending", "Country", "SP500", "GDP", "user_id"]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    for field in required_fields:
        params.append(data[field])
    cursor.execute(query, params)

    conn.commit()
    saved_id = cursor.lastrowid
    cursor.close()
    return jsonify({'message': 'Policy saved successfully', 'saved_id': saved_id}), 200

@politician.route("/policy/<int:user_id>", methods=["GET"])
def get_policy(user_id):
    conn = db.get_db()
    cursor = conn.cursor()

    cursor.execute(f'SELECT saved_id FROM SavedPolicy WHERE user_id = {user_id}')
    result = cursor.fetchall()

    conn.commit()
    cursor.close()

    return jsonify(result), 200