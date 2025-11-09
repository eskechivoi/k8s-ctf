import os
from app import create_app
from pathlib import Path

PARENT_CHART_PATH = os.environ.get('PARENT_CHART_PATH', '/app/challenge-commons')
CHARTS_STORAGE_DIR = os.path.join(PARENT_CHART_PATH, 'charts')
CHART_YAML_PATH = os.path.join(PARENT_CHART_PATH, 'Chart.yaml')

app = create_app(PARENT_CHART_PATH, CHARTS_STORAGE_DIR)

@app.before_first_request
def initialize_environment():
    Path(PARENT_CHART_PATH).mkdir(exist_ok=True)
    Path(CHARTS_STORAGE_DIR).mkdir(exist_ok=True)
    app.logger.info(f"Parent chart path configured: {PARENT_CHART_PATH}")
    app.logger.info(f"Chart storage path configured: {CHARTS_STORAGE_DIR}")


if __name__ == '__main__':
    # This is only used for local development (not used by guvicorn)
    initialize_environment() 
    app.run(debug=True, host='0.0.0.0', port=5000)