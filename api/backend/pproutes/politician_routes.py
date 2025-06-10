from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

politician = Blueprint("politician", __name__)


@politician.route("/fetchall/<int:user_id>", methods=["GET"])
def fetch_all(user_id):
    conn = db.get_db()
    cursor = conn.cursor()

    query = "SELECT politician_id, full_name FROM Politicians WHERE user_id = " + \
        str(user_id)
    cursor.execute(query)
    allnames = cursor.fetchall()
    return jsonify(allnames), 200


@politician.route("/getID/<polName>", methods=["GET"])
def get_id(polName):
    conn = db.get_db()
    cursor = conn.cursor()

    query = "SELECT politician_id FROM Politicians WHERE full_name = %s"
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
    INSERT INTO Politicians (full_name, contact_info, user_id)
    VALUES
    (%s, %s, %s)
    """
    params = []

    req = request.get_json()
    required_fields = ["full_name", "contact", "user_id"]
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
