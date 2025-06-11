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
    
    # Get range parameters
    budget_min = request.args.get('budget_min', None)
    budget_max = request.args.get('budget_max', None)
    duration_min = request.args.get('duration_min', None)
    duration_max = request.args.get('duration_max', None)
    population_min = request.args.get('population_min', None)
    population_max = request.args.get('population_max', None)

    # Debug logging
    current_app.logger.info(f"Query parameters: budget_min={budget_min}, budget_max={budget_max}, duration_min={duration_min}, duration_max={duration_max}, population_min={population_min}, population_max={population_max}")

    # Validate order param
    if order not in ('ASC', 'DESC'):
        order = 'ASC'

    # Build base query
    query = "SELECT policy_id, year_enacted, politician, topic, country, budget, duration_length, population_size FROM Policies"
    params = []
    conditions = []

    # Add filtering if year specified
    if year_start:
        conditions.append("year_enacted >= %s")
        params.append(year_start)
    if year_end:
        conditions.append("year_enacted <= %s")
        params.append(year_end)
    if country:
        conditions.append("country = %s")
        params.append(country)
    if topic:
        conditions.append("topic = %s")
        params.append(topic)
    if politician:
        conditions.append("politician = %s")
        params.append(politician)

    # Add numeric range conditions
    if budget_min is not None:
        conditions.append("(budget IS NULL OR budget >= %s)")
        params.append(float(budget_min))  # Convert to float to handle larger numbers
    if budget_max is not None:
        conditions.append("(budget IS NULL OR budget <= %s)")
        params.append(float(budget_max))  # Convert to float to handle larger numbers
    
    if duration_min is not None:
        conditions.append("(duration_length IS NULL OR duration_length >= %s)")
        params.append(int(duration_min))
    if duration_max is not None:
        conditions.append("(duration_length IS NULL OR duration_length <= %s)")
        params.append(int(duration_max))
    
    if population_min is not None:
        conditions.append("(population_size IS NULL OR population_size >= %s)")
        params.append(int(population_min))
    if population_max is not None:
        conditions.append("(population_size IS NULL OR population_size <= %s)")
        params.append(int(population_max))

    # Add WHERE clause if there are any conditions
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += f" ORDER BY {sort_by} {order}"

    # Debug logging
    current_app.logger.info(f"Final query: {query}")
    current_app.logger.info(f"Query parameters: {params}")

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