from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

policy_api = Blueprint("policy_api", __name__)

@policy_api.route("/general_info", methods=["GET"])
def test():
    cursor = db.get_db().cursor()
    current_app.logger.info("testing testing.")
    query = "SELECT * FROM Policies"
    cursor.execute(query)  
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

@policy_api.route("/policy_handler", methods=["GET"])
def get_policies():
    cursor = db.get_db().cursor()
    sort_by = request.args.get('sort_by', 'policy_id')
    order = request.args.get('order', 'ASC').upper()
    year_start = request.args.get('Start Year', None)
    year_end = request.args.get('End Year', None)
    country = request.args.get('country_choice', None)
    topic = request.args.get('Topic Choice', None)
    politician = request.args.get('politician_choice', None)
    if order not in ('ASC', 'DESC'):
        order = 'ASC'
    query = "SELECT policy_id, year_enacted, politician, topic, country FROM Policies"
    params = []
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


@policy_api.route("/favorites/<int:user_id>", methods=["GET"])
def getfav(user_id):
    conn = db.get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM Policies JOIN Favorite_Policies ON Favorite_Policies.policy_id = Policies.policy_id WHERE Favorite_Policies.user_id = " + str(user_id)
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)


@policy_api.route("/favorites", methods=["POST"])
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

@policy_api.route("/all_favorites", methods=["GET"])
def getallfav():
    cursor = db.get_db().cursor()
    current_app.logger.info("testing testing.")
    query = "SELECT * FROM Favorite_Policies"
    cursor.execute(query)  
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

@policy_api.route("/description/<int:policy_id>", methods=["GET"])
def getdesc(policy_id):
    conn = db.get_db()
    cursor = db.get_db().cursor()
    current_app.logger.info("testing testing.")
    query = "SELECT pol_description FROM Favorite_Policies WHERE policy_id = %s"
    params = [policy_id]
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    return jsonify(data)

@policy_api.route("/favorites/<int:policy_id>", methods=["DELETE"])
def deletefav(policy_id):
    conn = db.get_db()
    cursor = db.get_db().cursor()
    current_app.logger.info("testing testing.")
    cursor.execute("DELETE FROM Favorite_Policies WHERE policy_id = %s", str(policy_id))
    conn.commit()
    conn.commit()
    cursor.close()
    return '', 200

@policy_api.route("/politician/<int:policy_id>", methods=["GET"])
def get_contact_info(policy_id):
    conn = db.get_db()
    cursor = conn.cursor()
    query = f"SELECT * FROM Policies JOIN Politicians ON Policies.politician = Politicians.full_name WHERE Policies.policy_id = {policy_id}"
    cursor.execute(query)
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    return jsonify(data), 200