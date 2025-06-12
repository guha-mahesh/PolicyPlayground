from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

politician = Blueprint("politician", __name__)


@politician.route("/politicians/<int:user_id>", methods=["GET"])
def fetch_all(user_id):
    conn = db.get_db()
    cursor = conn.cursor()

    query = "SELECT politician_id, full_name, email_address, phone_number, department FROM Politicians WHERE user_id = " + \
        str(user_id)
    cursor.execute(query)
    allnames = cursor.fetchall()
    return jsonify(allnames), 200


@politician.route("/newPolitician", methods=["POST"])
def new_politician():
    conn = db.get_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO Politicians (full_name, email_address, phone_number, department, user_id)
    VALUES
    (%s, %s, %s, %s, %s)
    """
    params = []

    req = request.get_json()
    required_fields = ["full_name", "email_address", "phone_number", "department", "user_id"]
    for field in required_fields:
        if field not in req:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    for field in required_fields:
        params.append(req[field])
    cursor.execute(query, params)

    polId = cursor.lastrowid
    conn.commit()
    cursor.close()
    return jsonify({"message": "Politician created successfully", "polID": polId}, 201)


@politician.route("/policy", methods=["POST"])
def savePolicy():
    conn = db.get_db()
    cursor = conn.cursor()
    data = request.get_json()

    query = """
            INSERT INTO SavedPolicy (discountRate, FederalReserveBalanceSheet, TreasurySecurities,
            FederalFundsRate, MoneySupply, ReserveRequirementRatio,
            HealthSpending, MilitarySpending, EducationSpending, InfrastructureSpending,
            DebtToGDPRatio, CorporateTaxRate, Country, SP500, GDP, user_id, title)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    params = []

    required_fields = ["discountRate", "federalReserveBalanceSheet",
                       "treasurySecurities", "federalFundsRate", "moneySupply", 
                       "reserveRequirementRatio", "healthSpending", "militarySpending",
                       "educationSpending", "infrastructureSpending", "debtToGDPRatio",
                       "corporateTaxRate", "country", "market_index", "GDP", "user_id", "title"]
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    for field in required_fields:
        params.append(data[field])
    cursor.execute(query, params)

    conn.commit()
    saved_id = cursor.lastrowid
    cursor.close()
    return jsonify({'message': 'Policy saved successfully', 'saved_id': saved_id}), 200

@politician.route("/policy", methods=["PUT"])
def modifyPolicy():
    conn = db.get_db()
    cursor = conn.cursor()
    data = request.get_json()

    query = """
            UPDATE SavedPolicy 
            SET discountRate = %s, 
                FederalReserveBalanceSheet = %s, 
                TreasurySecurities = %s,
                FederalFundsRate = %s, 
                MoneySupply = %s, 
                ReserveRequirementRatio = %s,
                HealthSpending = %s, 
                MilitarySpending = %s, 
                EducationSpending = %s, 
                InfrastructureSpending = %s,
                DebtToGDPRatio = %s, 
                CorporateTaxRate = %s, 
                Country = %s, 
                SP500 = %s, 
                GDP = %s, 
                title = %s
                WHERE user_id = %s AND saved_id = %s"""

    params = []

    required_fields = ["discountRate", "federalReserveBalanceSheet",
                       "treasurySecurities", "federalFundsRate", "moneySupply", 
                       "reserveRequirementRatio", "healthSpending", "militarySpending",
                       "educationSpending", "infrastructureSpending", "debtToGDPRatio",
                       "corporateTaxRate", "country", "market_index", "GDP", "title", "user_id", "saved_id"]
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    for field in required_fields:
        params.append(data[field])
    cursor.execute(query, params)

    conn.commit()
    saved_id = cursor.lastrowid
    cursor.close()
    return jsonify({'message': 'Policy saved successfully', 'saved_id': saved_id}), 200

@politician.route("/allpolicy/<int:user_id>", methods=["GET"])
def get_policy(user_id):
    conn = db.get_db()
    cursor = conn.cursor()

    cursor.execute(
        f'SELECT saved_id FROM SavedPolicy WHERE user_id = {user_id}')
    result = cursor.fetchall()

    conn.commit()
    cursor.close()

    return jsonify(result), 200


@politician.route("/policy/<int:saved_id>", methods=["GET"])
def get_saved(saved_id):
    conn = db.get_db()
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM SavedPolicy WHERE saved_id = {saved_id}')
    result = cursor.fetchall()

    conn.commit()
    cursor.close()

    return jsonify(result), 200


@politician.route("/publisher", methods=["POST"])
def publish_policy():
    conn = db.get_db()
    cursor = conn.cursor()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        current_app.logger.info(f"Received publish request with data: {data}")
        
        if 'saved_id' not in data or 'user_id' not in data:
            return jsonify({"error": "Missing required fields: saved_id and user_id are required"}), 400
            
        check_query = """
        SELECT publish_id FROM PublishPolicy 
        WHERE saved_id = %s
        """
        cursor.execute(check_query, (data['saved_id'],))
        existing = cursor.fetchone()
        
        if existing:
            return jsonify({"error": "Policy is already published"}), 400

        query = """
        INSERT INTO PublishPolicy (saved_id, user_id)
        VALUES (%s, %s)
        """
        params = [data['saved_id'], data['user_id']]
        
        cursor.execute(query, params)
        publish_id = cursor.lastrowid
        conn.commit()
        
        current_app.logger.info(f"Successfully published policy with ID: {publish_id}")
        return jsonify({"message": "Policy published successfully", "publish_id": publish_id}), 201
        
    except Exception as e:
        current_app.logger.error(f"Error publishing policy: {str(e)}")
        conn.rollback()
        return jsonify({"error": f"Failed to publish policy: {str(e)}"}), 500
    finally:
        cursor.close()


@politician.route("/publisher", methods=["GET"])
def get_published_policies():
    conn = db.get_db()
    cursor = conn.cursor()

    query = """
    SELECT p.*, s.* 
    FROM PublishPolicy p
    JOIN SavedPolicy s ON p.saved_id = s.saved_id
    ORDER BY p.publish_date DESC
    """
    
    try:
        cursor.execute(query)
        policies = cursor.fetchall()
        return jsonify(policies), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@politician.route("/userPublisher/<int:user_id>", methods=["GET"])
def get_user_published_policies(user_id):
    conn = db.get_db()
    cursor = conn.cursor()

    query = """
    SELECT p.publish_id, p.saved_id, s.title 
    FROM PublishPolicy p 
    JOIN SavedPolicy s ON p.saved_id = s.saved_id
    WHERE p.user_id = %s
    ORDER BY p.publish_date DESC
    """
    
    try:
        cursor.execute(query, (user_id,))
        policies = cursor.fetchall()
        return jsonify(policies), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()



@politician.route("/publisher/<int:publish_id>", methods=["DELETE"])
def unpublish_policy(publish_id):
    conn = db.get_db()
    cursor = conn.cursor()

    query = """
    DELETE FROM PublishPolicy
    WHERE publish_id = %s
    """
    
    try:
        cursor.execute(query, (publish_id,))
        conn.commit()
        return jsonify({"message": "Policy unpublished successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@politician.route("/all_published/<int:saved_id>", methods=["GET"])
def check_published(saved_id):
    conn = db.get_db()
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT publish_id FROM PublishPolicy 
        WHERE saved_id = %s
        """
        cursor.execute(query, (saved_id,))
        result = cursor.fetchone()
        
        return jsonify({"is_published": result is not None}), 200
    except Exception as e:
        current_app.logger.error(f"Error checking publication status: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
