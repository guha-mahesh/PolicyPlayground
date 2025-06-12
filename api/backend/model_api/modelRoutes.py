from flask import (
    Blueprint,
    request,
    jsonify,
    make_response,
    current_app,
    redirect,
    url_for,
)
import json


from ..db_connection import db
from ..ml_models.model01_GDP import train_func, predict
from ..ml_models.model02_American import predict_sp500, predict_currency, train
import datetime
from backend.ml_models.model03_SimilarPolicies import predict as predict_similar_policies


model_routes = Blueprint("modelRoutes", __name__)


@model_routes.route("/")
def welcome():
    current_app.logger.info("GET / handler")
    welcome_message = "<h1>Welcome to the CS 3200 Project Template REST API"
    response = make_response(welcome_message)
    response.status_code = 200
    return response


@model_routes.route("/SP500/<var_01>", methods=["GET"])
def get_predictionSp500(var_01):
    current_app.logger.info("GET /prediction handler")

    try:

        user_features = [float(x.strip()) for x in var_01.split(',')]

        prediction = predict_sp500(user_features)

        current_app.logger.info(f"prediction value returned is {prediction}")

        response_data = {
            "prediction": prediction,
            "input_variables": {
                "var01": var_01,
            },
        }

        response = make_response(jsonify(response_data))
        response.status_code = 200
        return response

    except Exception as e:

        current_app.logger.error(f"Error: {str(e)}")
        response = make_response(
            jsonify({"error": f"Error processing prediction request: {str(e)}"})
        )
        response.status_code = 500
        return response


@model_routes.route("/currency/<var_01>", methods=["GET"])
def get_predictionCurr(var_01):
    current_app.logger.info("GET /prediction handler")

    try:

        user_features = [float(x.strip()) for x in var_01.split(',')]

        prediction = predict_currency(user_features)

        current_app.logger.info(f"prediction value returned is {prediction}")

        response_data = {
            "prediction": prediction,
            "input_variables": {
                "var01": var_01,
            },
        }

        response = make_response(jsonify(response_data))
        response.status_code = 200
        return response

    except Exception as e:

        current_app.logger.error(f"Error: {str(e)}")
        response = make_response(
            jsonify({"error": f"Error processing prediction request: {str(e)}"})
        )
        response.status_code = 500
        return response


@model_routes.route("/GDP/<var_01>/<var_02>", methods=["GET"])
def get_predictionGDP(var_01, var_02):
    current_app.logger.info("GET /prediction handler")

    try:

        user_features = [float(x.strip()) for x in var_01.split(',')]

        prediction = predict(user_features, var_02)

        current_app.logger.info(f"prediction value returned is {prediction}")

        response_data = {
            "prediction": prediction,
            "input_variables": {
                "var01": var_01,
            },
        }

        response = make_response(jsonify(response_data))
        response.status_code = 200
        return response

    except Exception as e:

        current_app.logger.error(f"Error: {str(e)}")
        response = make_response(
            jsonify({"error": f"Error processing prediction request: {str(e)}"})
        )
        response.status_code = 500
        return response


@model_routes.route("/data/<var01>", methods=["GET"])
def fetchalldata(var01):
    cursor = db.get_db().cursor()
    query = f"SELECT mos, vals FROM {var01}"
    cursor.execute(query)

    rows = cursor.fetchall()
    cursor.close()

    if rows and isinstance(rows[0], dict):

        data = rows
    else:

        data = [{'mos': row[0], 'vals': row[1]} for row in rows]

    return jsonify({
        'data': data,
    })


@model_routes.route("/data2/<var01>", methods=["GET"])
def fetchalldata2(var01):
    cursor = db.get_db().cursor()
    query = f"SELECT country, mos, vals FROM {var01}"
    cursor.execute(query)

    rows = cursor.fetchall()
    cursor.close()

    if rows and isinstance(rows[0], dict):

        data = rows
    else:

        data = [{'country': row[0], 'mos': row[1], 'vals': row[2]}
                for row in rows]

    return jsonify({
        'data': data,
    })


@model_routes.route("/models", methods=["POST"])
def trainModels():
    results = train()
    results2 = train_func()

    return jsonify({
        'status': 'success',
        'message': 'Models trained successfully',
    }), 200


@model_routes.route("/weights", methods=["POST"])
def storeWeights():
    try:
        data = request.json
        model_name = data.get('model_name')
        coefficients = data.get('coefficients')
        if not model_name or not coefficients:
            return jsonify({'error': 'Missing model_name or coefficients'}), 400
        coefficients_str = ','.join(map(str, coefficients))
        cursor = db.get_db().cursor()
        query = "INSERT INTO model_weights (model_name, coefficients) VALUES (%s, %s)"
        cursor.execute(query, (model_name, coefficients_str))
        db.get_db().commit()
        cursor.close()

        return jsonify({
            'status': 'success',
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@model_routes.route("/weights/<model_name>", methods=["GET"])
def get_weights(model_name):
    try:
        cursor = db.get_db().cursor()

        query = """
            SELECT coefficients 
            FROM model_weights 
            WHERE model_name = %s 
            ORDER BY id DESC 
            LIMIT 1
        """
        cursor.execute(query, (model_name,))
        result = cursor.fetchone()
        cursor.close()

        if result:

            if isinstance(result, dict):
                coefficients_str = result['coefficients']
            else:
                coefficients_str = result[0]

            coefficients = [float(x) for x in coefficients_str.split(',')]

            return jsonify({
                'model_name': model_name,
                'coefficients': coefficients
            }), 200
        else:
            return jsonify({'error': f'No weights found for model: {model_name}'}), 404

    except Exception as e:
        pass


@model_routes.route("/similar_policies/<int:index_policy>", methods=["GET"])
def get_similar_policies(index_policy):
    try:
        policies_list = predict_similar_policies(index_policy)

        return jsonify(policies_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@model_routes.route("/countryGDP/<country>", methods=["GET"])
def fetchData(country):
    cursor = db.get_db().cursor()
    cursor.execute(
        "SELECT vals, mos, country FROM GDP WHERE country = %s", (country,))
    result = cursor.fetchall()

    cursor.close()
    gdp_data = []

    for row in result:
        gdp_data.append({
            'vals': row['vals'],
            'mos': row['mos'],
            'country': row['country']
        })

    return jsonify({
        'success': True,
        'data': gdp_data,
        'count': len(gdp_data)
    }), 200
