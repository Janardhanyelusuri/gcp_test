import os
from flask import Flask, jsonify
from google.cloud import secretmanager

app = Flask(__name__)

# Initialize Secret Manager client
secret_client = secretmanager.SecretManagerServiceClient()

def get_secret(secret_name):
    """
    Retrieve secret from Google Secret Manager
    
    Args:
        secret_name: Name of the secret (e.g., 'db-password')
    
    Returns:
        Secret value as string, or None if error
    """
    try:
        project_id = os.environ.get('GCP_PROJECT_ID') or os.environ.get('GOOGLE_CLOUD_PROJECT')
        
        if not project_id:
            app.logger.error("GCP_PROJECT_ID not set in environment")
            return None
        
        # Build the resource name
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        
        # Access the secret
        response = secret_client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode('UTF-8')
        
        app.logger.info(f"Successfully retrieved secret: {secret_name}")
        return secret_value
        
    except Exception as e:
        app.logger.error(f"Error retrieving secret {secret_name}: {str(e)}")
        return None

# Cache secrets on startup (optional - improves performance)
DB_PASSWORD = None
API_KEY = None

def initialize_secrets():
    """Load secrets on application startup"""
    global DB_PASSWORD, API_KEY
    
    app.logger.info("Initializing secrets from Secret Manager...")
    
    DB_PASSWORD = get_secret('db-password')
    API_KEY = get_secret('api-key')
    
    if DB_PASSWORD:
        app.logger.info("DB_PASSWORD loaded successfully")
    else:
        app.logger.warning("DB_PASSWORD not loaded")
    
    if API_KEY:
        app.logger.info("API_KEY loaded successfully")
    else:
        app.logger.warning("API_KEY not loaded")

# Health check endpoint (required for App Engine health checks)
@app.route("/health")
def health_check():
    """Health check endpoint for App Engine liveness/readiness probes"""
    return jsonify({
        "status": "healthy",
        "service": "flask-app",
        "environment": os.environ.get('ENVIRONMENT', 'unknown')
    }), 200

# Root endpoint
@app.route("/")
def hello():
    """Main application endpoint"""
    try:
        # Use cached secrets or fetch them
        db_password = DB_PASSWORD or get_secret('db-password')
        api_key = API_KEY or get_secret('api-key')
        
        return (
            "Hello from GitHub → Cloud Build → App Engine!\n\n"
            f"Environment: {os.environ.get('ENVIRONMENT', 'unknown')}\n"
            f"DB_PASSWORD loaded: {'✓ yes' if db_password else '✗ no'}\n"
            f"API_KEY loaded: {'✓ yes' if api_key else '✗ no'}\n\n"
            "App is running in production mode with Secret Manager integration.\n"
        ), 200
        
    except Exception as e:
        app.logger.error(f"Error in main route: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "Check application logs for details"
        }), 500

# API endpoint example (using secrets)
@app.route("/api/status")
def api_status():
    """API status endpoint showing configuration"""
    try:
        return jsonify({
            "status": "operational",
            "environment": os.environ.get('ENVIRONMENT', 'unknown'),
            "secrets_configured": {
                "db_password": DB_PASSWORD is not None,
                "api_key": API_KEY is not None
            },
            "project_id": os.environ.get('GCP_PROJECT_ID', 'not-set')
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error in status endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Not Found",
        "message": "The requested endpoint does not exist"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }), 500

# Initialize secrets when app starts
with app.app_context():
    initialize_secrets()

if __name__ == "__main__":
    # This is only used for local development
    # In production, gunicorn is used (specified in app.yaml)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
