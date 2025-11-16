import os
from app import create_app
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
app_logger = logging.getLogger('ctf-api')

CHALLENGES_NAMESPACE = os.environ.get('CHALLENGES_NAMESPACE', '/app/challenge-commons')
PARENT_CHART_PATH = os.environ.get('PARENT_CHART_PATH', '/app/challenge-commons')
CHARTS_STORAGE_DIR = os.path.join(PARENT_CHART_PATH, 'charts')

app = create_app(CHALLENGES_NAMESPACE, PARENT_CHART_PATH, CHARTS_STORAGE_DIR)

try:
    Path(PARENT_CHART_PATH).mkdir(exist_ok=True)
    Path(CHARTS_STORAGE_DIR).mkdir(exist_ok=True)
    app_logger.info(f"Parent chart path configured: {PARENT_CHART_PATH}")
    app_logger.info(f"Chart storage path configured: {CHARTS_STORAGE_DIR}")
except Exception as e:
    app_logger.error(f"Error during directory initialization: {e}")

if __name__ == '__main__':
    # This is only used for local development (not used by guvicorn)
    app.run(debug=True, host='0.0.0.0', port=5000)