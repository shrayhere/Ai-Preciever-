import os
from flask import Flask
from config import Config
from database.db import init_db
from routes.main_routes import main_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize SQLite database schema
    init_db()

    # Register blueprint
    app.register_blueprint(main_bp)

    return app

app = create_app()

if __name__ == "__main__":
    print("Starting DeepVerify server on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
