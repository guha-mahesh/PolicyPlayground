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




    

