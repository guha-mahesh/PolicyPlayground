from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app


# Create a Blueprint for NGO routes
policy_api = Blueprint("policy_api", __name__)

@policy_api.route("/get", methods=["GET"])
def test():
    response = {
        "the_joke" : "Knock Knock!", "id" :5
        }
    
    
    conn = db.get_db()
    cursor = conn.cursor()
    current_app.logger.info("testing testing.")
    cursor.execute("SELECT * FROM Policies")  # Replace with your table name
    rows = cursor.fetchall()
    
    # Convert the rows to a list of dicts
    data = [dict(row) for row in rows]

    conn.close()
    return jsonify(data)

    return jsonify(response)

    

