from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

users = Blueprint("users", __name__)

@users.route("/getUser/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = db.get_db()
    cursor = conn.cursor()

    query = """SELECT * FROM Users WHERE user_id = %s"""
    params = [user_id]
    cursor.execute(query, params)
    returnJson = cursor.fetchall()

    conn.commit()
    cursor.close()
    return jsonify(returnJson), 200