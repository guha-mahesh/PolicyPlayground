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
from backend.db_connection import db
from backend.simple.playlist import sample_playlist_data
from backend.ml_models.model01_GDP import predict_gdp
from backend.ml_models.model02_American import predict_sp500, predict_currency, train
import datetime


model_routes = Blueprint("modelRoutes", __name__)


@model_routes.route("/")
def welcome():
    current_app.logger.info("GET / handler")
    welcome_message = "<h1>Welcome to the CS 3200 Project Template REST API"
    response = make_response(welcome_message)
    response.status_code = 200
    return response


@model_routes.route("/predictSp/<var_01>", methods=["GET"])
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


@model_routes.route("/predictCurr/<var_01>", methods=["GET"])
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


@model_routes.route("/predictGDP/<var_01>/<var_02>", methods=["GET"])
def get_predictionGDP(var_01, var_02):
    current_app.logger.info("GET /prediction handler")

    try:

        user_features = [float(x.strip()) for x in var_01.split(',')]

        prediction = predict_gdp(user_features, var_02)

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


@model_routes.route("/fetchAllData/<var01>", methods=["GET"])
def fetchalldata(var01):
    cursor = db.get_db().cursor()
    query = f"SELECT date, value FROM {var01}"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)


@model_routes.route("/saveWeights", methods=["GET"])
def saveWeights():
    weights = train()
    cursor = db.get_db().cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_weights (
                id INTEGER PRIMARY KEY,
                sp500_weights TEXT,
                currency_weights TEXT,
                created_at TIMESTAMP
            )
        """)

    cursor.execute("""
       INSERT OR REPLACE INTO model_weights (id, sp500_weights, currency_weights, created_at)
       VALUES (1, ?, ?, ?)
   """, (
        json.dumps(weights['sp500_weights']),
        json.dumps(weights['currency_weights']),
        datetime.datetime.now()
    ))
    db.get_db().commit()
    cursor.close()

    return {"status": "success", "message": "Weights saved"}


@model_routes.route("/getWeights", methods=["GET"])
def getWeights():
    cursor = db.get_db().cursor()

    cursor.execute("""
        SELECT sp500_weights, currency_weights, created_at 
        FROM model_weights 
        WHERE id = 1
    """)

    result = cursor.fetchone()
    cursor.close()

    if result:
        return {
            "sp500_weights": json.loads(result[0]),
            "currency_weights": json.loads(result[1]),
        }
