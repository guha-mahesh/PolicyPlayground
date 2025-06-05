from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

notes = Blueprint("notes", __name__)


@notes.route("/addnote", methods=["POST"])
def add_note():
    conn = db.get_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO Conversations (politician_id, content, title, user_id)
    VALUES
    (%s, %s, %s, %s)
    """
    params = []

    req = request.get_json()
    required_fields = ["politician_id", "content", "title", "user_id"]
    for field in required_fields:
        if field not in req:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    for field in required_fields:
        params.append(req[field])
    cursor.execute(query, params)

    noteid = cursor.lastrowid
    conn.commit()
    cursor.close()
    return jsonify({"message": "Note created successfully", "note_id": noteid}, 201)

@notes.route("/showNotes", methods=["GET"])
def all_notes():
    conn = db.get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM Conversations WHERE user_id = %s"
    cursor.execute(query)
    returnjson = cursor.fetchall()

    conn.commit()
    cursor.close()

    return jsonify(returnjson), 200