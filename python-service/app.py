
from flask import Flask, jsonify
from api import api_bp

app = Flask(__name__)
app.register_blueprint(api_bp)


# Global error handler to always return JSON
@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    response = {
        "intent": "error",
        "results": None,
        "error": str(e),
        "trace": traceback.format_exc()
    }
    return jsonify(response), 500

# JSON error handler for 404 Not Found
@app.errorhandler(404)
def handle_404(e):
    response = {
        "intent": "error",
        "results": None,
        "error": "Not Found",
        "message": str(e)
    }
    return jsonify(response), 404

# JSON error handler for 405 Method Not Allowed
@app.errorhandler(405)
def handle_405(e):
    response = {
        "intent": "error",
        "results": None,
        "error": "Method Not Allowed",
        "message": str(e)
    }
    return jsonify(response), 405

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("flask-app")
    logger.info("[Python Flask] Starting Flask app on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000)
