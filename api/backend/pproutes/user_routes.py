from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

users = Blueprint("users", __name__)

@users.route("/getuser", methods=["GET"])
def get_user():
    conn = db.get_db()
    cursor = conn.cursor()
    return