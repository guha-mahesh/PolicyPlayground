from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

politician = Blueprint("politician", __name__)


@politician.route("/fetchall", methods=["GET"])
def fetch_all():
    # conn = db.get_db()
    # cursor = conn.cursor()

    # query = "SELECT Name FROM Politicians"

    # cursor.execute()
    return