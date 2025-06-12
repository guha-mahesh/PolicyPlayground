from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

notes = Blueprint("notes", __name__)


@notes.route("/note", methods=["POST"])
def add_note():
    conn = db.get_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO Conversations (politician_id, content, title, user_id, saved_id)
    VALUES
    (%s, %s, %s, %s, %s)
    """
    params = []

    req = request.get_json()
    required_fields = ["politician_id", "content", "title", "user_id", "saved_id"]
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

@notes.route("/notes/<int:user_id>/<int:politician_id>", methods=["GET"])
def all_notes(user_id, politician_id):
    conn = db.get_db()
    cursor = conn.cursor()

    query = f'SELECT * FROM Conversations WHERE user_id = {user_id} AND politician_id = {politician_id}'
    cursor.execute(query)
    returnjson = cursor.fetchall()

    conn.commit()
    cursor.close()

    return jsonify(returnjson), 200

@notes.route("/note", methods=["PUT"])
def modify_note():
    conn = db.get_db()
    cursor = conn.cursor()

    query = "UPDATE Conversations SET title = %s, content = %s WHERE conversation_id = %s AND user_id = %s"
    params = []

    req = request.get_json()
    required_fields = ["title", "content", "conversation_id", "user_id"]
    for field in required_fields:
        if field not in req:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    for field in required_fields:
        params.append(req[field])
        
    cursor.execute(query, params)
    returnjson = cursor.fetchall()

    conn.commit()
    cursor.close()

    return jsonify(returnjson), 200

@notes.route("/policy/<int:conversation_id>", methods=["GET"])
def saved_policy(conversation_id):
    conn = db.get_db()
    cursor = conn.cursor()

    query = f'SELECT saved_id FROM Conversations WHERE conversation_id = {conversation_id}'
    cursor.execute(query)
    returnjson = cursor.fetchall()

    conn.commit()
    cursor.close()

    return jsonify(returnjson), 200