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

@politician.route("/showNotes", methods=["GET"])
def all_notes():
    conn = db.get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM Conversations"
    cursor.execute(query)
    returnjson = cursor.fetchall()

    conn.commit()
    cursor.close()

    return jsonify(returnjson), 200