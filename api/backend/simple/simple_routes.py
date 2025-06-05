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
from backend.ml_models.model02_American import predict_sp500, predict_currency


# This blueprint handles some basic routes that you can use for testing
simple_routes = Blueprint("simple_routes", __name__)


# ------------------------------------------------------------
# / is the most basic route
# Once the api container is started, in a browser, go to
# localhost:4000/playlist
@simple_routes.route("/")
def welcome():
    current_app.logger.info("GET / handler")
    welcome_message = "<h1>Welcome to the CS 3200 Project Template REST API"
    response = make_response(welcome_message)
    response.status_code = 200
    return response


# ------------------------------------------------------------
# /playlist returns the sample playlist data contained in playlist.py
# (imported above)
@simple_routes.route("/playlist")
def get_playlist_data():
    current_app.logger.info("GET /playlist handler")
    response = make_response(jsonify(sample_playlist_data))
    response.status_code = 200
    return response


# ------------------------------------------------------------
@simple_routes.route("/niceMesage", methods=["GET"])
def affirmation():
    message = """
    <H1>Think about it...</H1>
    <br />
    You only need to be 1% better today than you were yesterday!
    """
    response = make_response(message)
    response.status_code = 200
    return response


# ------------------------------------------------------------
# Demonstrates how to redirect from one route to another.
@simple_routes.route("/message")
def mesage():
    return redirect(url_for(affirmation))


@simple_routes.route("/data")
def getData():
    current_app.logger.info("GET /data handler")

    # Create a simple dictionary with nested data
    data = {"a": {"b": "123", "c": "Help"}, "z": {"b": "456", "c": "me"}}

    response = make_response(jsonify(data))
    response.status_code = 200
    return response


@simple_routes.route("/predictSp/<var_01>", methods=["GET"])
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


@simple_routes.route("/predictCurr/<var_01>", methods=["GET"])
def get_predictionCurr(var_01):
    current_app.logger.info("GET /prediction handler")

    try:
        # Parse the comma-separated input
        user_features = [float(x.strip()) for x in var_01.split(',')]

        # Call prediction function with parsed features
        # Pass the list, not the string
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
        # Add this to see the actual error
        current_app.logger.error(f"Error: {str(e)}")
        response = make_response(
            jsonify({"error": f"Error processing prediction request: {str(e)}"})
        )
        response.status_code = 500
        return response


@simple_routes.route("/predictGDP/<var_01>/<var_02>", methods=["GET"])
def get_predictionGDP(var_01, var_02):
    current_app.logger.info("GET /prediction handler")

    try:
        # Parse the comma-separated input
        user_features = [float(x.strip()) for x in var_01.split(',')]

        # Call prediction function with parsed features
        # Pass the list, not the string
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
        # Add this to see the actual error
        current_app.logger.error(f"Error: {str(e)}")
        response = make_response(
            jsonify({"error": f"Error processing prediction request: {str(e)}"})
        )
        response.status_code = 500
        return response
