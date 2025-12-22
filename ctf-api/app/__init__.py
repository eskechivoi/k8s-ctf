import os
from flask import Flask

def create_app(challenges_namespace, parent_chart_path, charts_storage_dir, gateway_namespace):
    """
    Factory function to initialize Flask app
    """
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit for uploaded files

    app.config['CHALLENGES_NAMESPACE'] = challenges_namespace
    app.config['PARENT_CHART_PATH'] = parent_chart_path
    app.config['CHARTS_STORAGE_DIR'] = charts_storage_dir
    app.config['CHART_YAML_PATH'] = os.path.join(parent_chart_path, 'Chart.yaml')
    app.config['GATEWAY_API_NAMESPACE'] = gateway_namespace

    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app