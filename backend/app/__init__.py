from flask import Flask
from flask_cors import CORS
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# MongoDB connection settings
MONGO_URI = os.getenv('DATABASE_URL', 'mongodb://localhost:27017/mywelthai')
app.config['MONGODB_SETTINGS'] = {
    'host': MONGO_URI,
    'connect': False,
}

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Connect to MongoDB
from app.database import connect_db
connect_db(host=MONGO_URI)

# Register blueprints (routes)
from app.routes import auth_routes, transaction_routes, dashboard_routes, advice_routes, analytics_routes, chatbot_routes, admin_routes, report_routes

app.register_blueprint(auth_routes.bp)
app.register_blueprint(transaction_routes.bp)
app.register_blueprint(dashboard_routes.bp)
app.register_blueprint(advice_routes.bp)
app.register_blueprint(analytics_routes.bp)
app.register_blueprint(chatbot_routes.chatbot_bp)
app.register_blueprint(admin_routes.bp)
app.register_blueprint(report_routes.bp)

print("[OK] MongoDB connection configured.")

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return {
        'message': 'Welcome to MyWelthAI Backend API',
        'status': 'running',
        'database': 'MongoDB',
        'endpoints': {
            'health': '/api/health',
            'auth': '/api/auth',
            'transactions': '/api/transactions',
            'dashboard': '/api/dashboard',
            'advice': '/api/advice'
        },
        'frontend': 'http://localhost:5174'
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'app': 'MyWelthAI Backend',
        'database': 'MongoDB'
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
