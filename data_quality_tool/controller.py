from flask import Flask, request, jsonify, send_file
import json
import logging
from io import BytesIO
import pandas as pd
from flask_cors import CORS
from converter.excel_to_json import convert_excel_to_json
from converter.json_to_excel import convert_json_to_excel
from validator import json_validator, excel_validator

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/")
def home():
    logger.info("Home endpoint accessed")
    return "Welcome to the Excel-JSON Converter API!"


@app.route("/excel-to-json", methods=["POST"])
def excel_to_json():
    logger.info("excel_to_json endpoint accessed")
    if "file" not in request.files:
        logger.error("No file part in request")
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        logger.error("No selected file")
        return jsonify({"error": "No selected file"}), 400
    if file:
        try:
            logger.info(f"Processing file: {file.filename}")
            file_stream = BytesIO(file.read())
            df = pd.read_excel(file_stream, engine="openpyxl")
            logger.info("Excel file read into DataFrame")
            excel_validator.validate_excel(df)
            logger.info("Excel file validated")
            json_data = convert_excel_to_json(df)
            logger.info("Excel file converted to JSON")
            pretty_json_data = json.dumps(json_data, indent=4)
            logger.info("JSON data pretty-printed")
            response = app.response_class(
                response=pretty_json_data, status=200, mimetype="application/json"
            )
            return response
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return jsonify({"error": str(e)}), 500


@app.route("/json-to-excel", methods=["POST"])
def json_to_excel():
    logger.info("json_to_excel endpoint accessed")
    if not request.json:
        logger.error("No JSON provided in request")
        return jsonify({"error": "No JSON provided"}), 400
    json_data = request.json
    try:
        logger.info(f"Processing JSON data: {json_data}")
        json_validator.validate_json(json_data)
        logger.info("JSON data validated")
        df = convert_json_to_excel(json_data)
        logger.info("JSON data converted to Excel")
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        logger.info("Excel file created and saved to buffer")
        return send_file(
            output,
            as_attachment=True,
            download_name="output.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        logger.error(f"Error processing JSON: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/validate-json", methods=["POST"])
def validate_json():
    logger.info("validate_json endpoint accessed")
    if not request.json:
        logger.error("No JSON provided in request")
        return jsonify({"error": "No JSON provided"}), 400
    json_data = request.json
    try:
        json_validator.validate_json(json_data)
        logger.info("JSON data is valid")
        return jsonify({"message": "Data model is valid."})
    except json_validator.InvalidDataModelError as e:
        logger.error(f"JSON validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400


@app.route("/validate-excel", methods=["POST"])
def validate_excel():
    logger.info("validate_excel endpoint accessed")
    if "file" not in request.files:
        logger.error("No file part in request")
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        logger.error("No selected file")
        return jsonify({"error": "No selected file"}), 400
    if file:
        try:
            logger.info(f"Processing file: {file.filename}")
            file_stream = BytesIO(file.read())
            df = pd.read_excel(file_stream, engine="openpyxl")
            logger.info("Excel file read into DataFrame")
            excel_validator.validate_excel(df)
            logger.info("Excel file is valid")
            return jsonify({"message": "Data model is valid."})
        except json_validator.InvalidDataModelError as e:
            logger.error(f"Excel validation error: {str(e)}")
            return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    logger.info("Starting Flask server...")
    app.run(host="0.0.0.0", port=8000)
