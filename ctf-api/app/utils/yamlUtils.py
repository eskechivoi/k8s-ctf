import yaml
from flask import current_app as app, abort
import os

def read_chart_yaml(file_path):
    """Reads and parses Chart.yaml."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        app.logger.warning(f"File not found in: {file_path}")
        return None
    except yaml.YAMLError as e:
        app.logger.error(f"Error parsing yaml in {file_path}: {e}")
        if os.path.exists(file_path):
            abort(500, description="Error reading Chart.yaml file.")
        return None

def write_chart_yaml(file_path, data):
    """Writes data back to Chart.yaml."""
    try:
        with open(file_path, 'w') as f:
            yaml.safe_dump(data, f, sort_keys=False)
    except Exception as e:
        app.logger.error(f"Error writting in file {file_path}: {e}")
        abort(500, description="Error saving file Chart.yaml.")

def add_dependency(file_path, new_dependency_config):
    """
    Adds or updates a dependency in the parent Chart.yaml using the real 
    metadata from the uploaded chart.
    
    :param file_path: Path to the parent Chart.yaml
    :param new_dependency_config: Dict containing 'name', 'version', etc.
    :return: The added dependency configuration.
    """
    
    # Read and update Chart.yaml
    chart_data = read_chart_yaml(file_path)
    
    if chart_data is None:
        chart_data = {
            'apiVersion': 'v2',
            'name': 'k8s-ctf-chart',
            'type': 'application',
            'description': 'Parent Chart for CTF challenges',
            'version': '0.1.0',
            'appVersion': '0.1.0',
            'dependencies': [],
            'annotations': {}
        }

    if 'annotations' not in chart_data:
        chart_data['annotations'] = {}

    dependencies = chart_data.get('dependencies', [])
    chart_name = new_dependency_config['name']
    custom_alias = new_dependency_config.pop('alias', chart_name)
    chart_data['annotations'][f'challenge.alias/{chart_name}'] = custom_alias
    if 'condition' not in new_dependency_config:
        new_dependency_config['condition'] = f'{chart_name}.enabled'

    dependencies = [d for d in dependencies if d.get('name') != chart_name]
    dependencies.append(new_dependency_config)
    
    chart_data['dependencies'] = dependencies
    
    write_chart_yaml(file_path, chart_data)
    new_dependency_config['annotations'][f'challenge.alias/{chart_name}'] = custom_alias
    return new_dependency_config