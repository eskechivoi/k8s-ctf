import os
import subprocess
import tarfile
from flask import current_app as app, jsonify, request
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
    Receives a compressed chart, saves it locally, reads its metadata, and 
    adds the dependency to the parent chart's Chart.yaml
    (POST /api/dependencies)
    """
    chart_file = request.files.get('chart_file')
    
    if not chart_file:
        return jsonify({"error": "Missing chart_file."}), 400
    
    charts_storage_dir = app.config['CHARTS_STORAGE_DIR']
    parent_chart_path = app.config['PARENT_CHART_PATH']
    chart_yaml_path = app.config['CHART_YAML_PATH']
    
    app.logger.info(f"Processing new chart")
    # --- 1. Save, Descompress and Obtain the Chart's path ---
    try:
        unpacked_chart_dir = save_chart(chart_file, charts_storage_dir)
        app.logger.info(f"Chart extracted to: {unpacked_chart_dir}")

        # --- 2. Read the Chart.yaml from the uploaded Chart
        uploaded_chart_yaml_path = os.path.join(unpacked_chart_dir, 'Chart.yaml')     
        uploaded_chart_data = read_chart_yaml(uploaded_chart_yaml_path)
        if not uploaded_chart_data:
             raise FileNotFoundError(f"Could not read Chart.yaml from the extracted path: {unpacked_chart_dir}")        
        real_chart_name = uploaded_chart_data.get('name')
        real_chart_version = uploaded_chart_data.get('version')  
        if not real_chart_name or not real_chart_version:
             raise ValueError("Chart.yaml in uploaded file is missing 'name' or 'version'.")
        app.logger.info(f"Read Chart details: Name={real_chart_name}, Version={real_chart_version}")
    except tarfile.TarError as e:
        app.logger.error(f"Error uncompressing the chart: {e}")
        return jsonify({"error": "Uploaded file is not a valid Helm tar.gz file or its structure is invalid."}), 400
    except (FileNotFoundError, ValueError) as e:
         app.logger.error(f"Error validating uploaded Chart: {e}")
         return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Internal error trying to save/extract the chart: {e}")
        return jsonify({"error": f"Internal error: {e}"}), 500

    # --- 3. Add new dependency to parent Chart ---
    new_dependency_config = {
        'name': real_chart_name,
        'version': real_chart_version,
    }
    try:
        new_dependency = add_dependency(chart_yaml_path, new_dependency_config)
    except Exception as e:
        app.logger.error(f"Error adding dependency to parent Chart.yaml: {e}")
        return jsonify({"error": f"Error updating parent Chart.yaml: {e}"}), 500

    # --- 4. Run helm dependency update ---
    try:
        app.logger.info(f"Running helm dependency update in {parent_chart_path}")
        result = update_dependencies(parent_chart_path)
        app.logger.info(f"Helm output: {result.stdout}")
        
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error in helm dependency update: {e.stderr}")
        return jsonify({
            "message": "Chart saved but failed while running helm dependency update.",
            "helm_error": e.stderr
        }), 500
        
    return jsonify({
        "message": f"Chart '{real_chart_name}' (v{real_chart_version}) saved and dependency successfully added.",
        "dependency_config": new_dependency
    }), 201
