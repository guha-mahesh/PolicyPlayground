from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app


# Create a Blueprint for NGO routes
policy_api = Blueprint("policy_api", __name__)

@policy_api.route("/get", methods=["GET"])
def test():
    
    cursor = db.get_db().cursor()
    current_app.logger.info("testing testing.")
    query = "SELECT * FROM Policies"
    params = []
    cursor.execute(query)  
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

@policy_api.route("/filter", methods=["GET"])
def filter():
    cursor = db.get_db().cursor()
    query = "SELECT * FROM Policies"
    cursor.execute(query)

    rows = cursor.fetchall()
    current_app.logger.info(rows)

    cursor.close()
    return jsonify(rows)


@policy_api.route("/getpol", methods=["GET"])
def get_policies():
    cursor = db.get_db().cursor()

    # Get query params (with defaults)
    sort_by = request.args.get('sort_by', 'policy_id')
    order = request.args.get('order', 'ASC').upper()
    year_start = request.args.get('Start Year', None)
    year_end = request.args.get('End Year', None)
    country = request.args.get('country_choice', None)
    topic = request.args.get('Topic Choice', None)
    politician = request.args.get('politician_choice', None)


    # Validate order param
    if order not in ('ASC', 'DESC'):
        order = 'ASC'

    # Build base query
    query = "SELECT policy_id, year_enacted, politician, topic, country FROM Policies"
    params = []

    # Add filtering if country specified
    if year_start:
        query += " WHERE year_enacted >= %s"
        params.append(year_start)

    if year_end:
        query += " AND year_enacted <= %s"
        params.append(year_end)

    if country:
        query += " AND country = %s"
        params.append(country)
    
    if topic:
        query += " AND topic = %s"
        params.append(topic)
    
    if politician:
        query += " AND politician = %s"
        params.append(politician)


    query += f" ORDER BY {sort_by} {order}"

    cursor.execute(query, params)
    data = cursor.fetchall()

    cursor.close()
    return jsonify(data)


@policy_api.route("/getfav/<int:user_id>", methods=["GET"])
def getfav(user_id):
    conn = db.get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM Policies JOIN Favorite_Policies ON Favorite_Policies.policy_id = Policies.policy_id WHERE Favorite_Policies.user_id = " + str(user_id)
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)


@policy_api.route("/add_favorite", methods=["POST"])
def add_favorite():
    conn = db.get_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO Favorite_Policies (policy_id, user_id)
    VALUES
    (%s, %s)
    """
    params = []

    req = request.get_json()
    required_fields = ["policy_id", "user_id"]
    for field in required_fields:
        if field not in req:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    for field in required_fields:
        params.append(req[field])
    cursor.execute(query, params)

    policy_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    return jsonify({"message": "Note created successfully", "policy_id": policy_id}, 201)

@policy_api.route("/getallfav", methods=["GET"])
def getallfav():
    cursor = db.get_db().cursor()
    current_app.logger.info("testing testing.")
    query = "SELECT * FROM Favorite_Policies"
    cursor.execute(query)  
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)