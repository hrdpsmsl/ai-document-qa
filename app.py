from flask import Flask
from config import Config
from extensions import db, jwt
from routes import routes
from services import qa_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register Blueprints
    app.register_blueprint(routes)
    app.register_blueprint(qa_bp)
    return app

if __name__ == '__main__':
    cert_path = os.path.join(os.path.dirname(__file__), 'cert', 'server.crt')
    key_path = os.path.join(os.path.dirname(__file__), 'cert', 'server.key')
    app = create_app()
    app.run(debug=True, ssl_context=(cert_path, key_path))
