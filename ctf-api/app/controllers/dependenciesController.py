import os
import subprocess
import tarfile
from flask import current_app as app, jsonify, request
from werkzeug.utils import secure_filename
from ..utils.yamlUtils import read_chart_yaml, add_dependency
from ..utils.tarUtils import save_chart
from ..utils.helmUtils import update_dependencies

def get_dependencies_controller():
    """
    Reads the Chart.yaml and returns the configured dependencies.
    (GET /api/dependencies)
    """
    chart_yaml_path = app.config['CHART_YAML_PATH']
    chart_data = read_chart_yaml(chart_yaml_path)

    if not chart_data:
        # Chart.yaml does not exist or has no dependencies
        return jsonify([])

    dependencies = chart_data.get('dependencies', [])
    app.logger.info(f"Read dependencies: {len(dependencies)}")
    return jsonify(dependencies)

def add_dependency_controller():
    """
    Receives a compressed chart, saves it locally and adds the dependency
    to the parent chart's Chart.yaml
    (POST /api/dependencies)
    """
    # Entry validation
    challenge_name = request.form.get('challenge_name')
    chart_file = request.files.get('chart_file')
    
    if not challenge_name or not chart_file:
        return jsonify({"error": "Missing challenge_name or chart_file."}), 400

    safe_name = secure_filename(challenge_name).lower()
    
    charts_storage_dir = app.config['CHARTS_STORAGE_DIR']
    parent_chart_path = app.config['PARENT_CHART_PATH']
    chart_yaml_path = app.config['CHART_YAML_PATH']
    
    app.logger.info(f"Processing new chart: {safe_name}")
    uploaded_file_path = os.path.join('/tmp', f'{safe_name}.tgz')

    # Save and uncompress the .tar chart into the charts subfold
    try:
        save_chart(chart_file, charts_storage_dir, safe_name)
    except tarfile.TarError as e:
        app.logger.error(f"Error uncompressing the chart: {e}")
        return jsonify({"error": "Uploaded file is not a valid tar.gz file."}), 400
    except Exception as e:
        app.logger.error(f"Error trying to save/extract the chart: {e}")
        return jsonify({"error": f"Internal error trying to save the file: {e}"}), 500
    finally:
        if os.path.exists(uploaded_file_path):
            os.remove(uploaded_file_path)

    # Add the new dependency
    new_dependency = add_dependency(chart_yaml_path, safe_name)

    # Run helm dependency update
    try:
        app.logger.info(f"Running helm dependency update in {parent_chart_path}")
        result = update_dependencies(parent_chart_path)
        app.logger.info(f"Helm output: {result.stdout}")
        
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error in helm dependency update: {e.stderr}")
        return jsonify({
            "message": "Chart saved but failing while running helm dependency update.",
            "helm_error": e.stderr
        }), 500
        
    return jsonify({
        "message": f"Chart '{challenge_name}' saved and dependency successfully added.",
        "dependency_config": new_dependency
    }), 201
