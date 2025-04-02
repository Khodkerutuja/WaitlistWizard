from flask import jsonify
from werkzeug.exceptions import HTTPException
from app import app
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Handle 400 Bad Request
@app.errorhandler(400)
def handle_bad_request(e):
    logger.error(f"400 Bad Request: {str(e)}")
    return jsonify({"error": "Bad Request", "message": str(e)}), 400

# Handle 401 Unauthorized
@app.errorhandler(401)
def handle_unauthorized(e):
    logger.error(f"401 Unauthorized: {str(e)}")
    return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401

# Handle 403 Forbidden
@app.errorhandler(403)
def handle_forbidden(e):
    logger.error(f"403 Forbidden: {str(e)}")
    return jsonify({"error": "Forbidden", "message": "You do not have permission to access this resource"}), 403

# Handle 404 Not Found
@app.errorhandler(404)
def handle_not_found(e):
    logger.error(f"404 Not Found: {str(e)}")
    return jsonify({"error": "Not Found", "message": "The requested resource was not found"}), 404

# Handle 405 Method Not Allowed
@app.errorhandler(405)
def handle_method_not_allowed(e):
    logger.error(f"405 Method Not Allowed: {str(e)}")
    return jsonify({"error": "Method Not Allowed", "message": "The method is not allowed for the requested URL"}), 405

# Handle 422 Unprocessable Entity
@app.errorhandler(422)
def handle_unprocessable_entity(e):
    logger.error(f"422 Unprocessable Entity: {str(e)}")
    return jsonify({"error": "Unprocessable Entity", "message": str(e)}), 422

# Handle 429 Too Many Requests
@app.errorhandler(429)
def handle_too_many_requests(e):
    logger.error(f"429 Too Many Requests: {str(e)}")
    return jsonify({"error": "Too Many Requests", "message": "Rate limit exceeded"}), 429

# Handle 500 Internal Server Error
@app.errorhandler(500)
def handle_internal_server_error(e):
    logger.error(f"500 Internal Server Error: {str(e)}")
    return jsonify({"error": "Internal Server Error", "message": "An internal server error occurred"}), 500

# Handle generic HTTP exceptions
@app.errorhandler(HTTPException)
def handle_http_exception(e):
    logger.error(f"HTTP Exception {e.code}: {str(e)}")
    return jsonify({"error": e.name, "message": str(e)}), e.code

# Handle generic exceptions
@app.errorhandler(Exception)
def handle_generic_exception(e):
    logger.error(f"Unhandled Exception: {str(e)}")
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500

# Database error handler
@app.errorhandler(Exception)
def handle_database_error(e):
    if "database" in str(e).lower() or "sql" in str(e).lower():
        logger.error(f"Database Error: {str(e)}")
        return jsonify({"error": "Database Error", "message": "A database error occurred"}), 500
    return handle_generic_exception(e)
