import yaml
from flask import current_app as app, abort

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
        abort(500, description="Error reading Chart.yaml file.")

def write_chart_yaml(file_path, data):
    """Writes data back to Chart.yaml."""
    try:
        with open(file_path, 'w') as f:
            yaml.safe_dump(data, f, sort_keys=False)
    except Exception as e:
        app.logger.error(f"Error writting in file {file_path}: {e}")
        abort(500, description="Error saving file Chart.yaml.")

def add_dependency(file_path, safe_name):
    # Read and update Chart.yaml
    chart_data = read_chart_yaml(file_path)
    
    if chart_data is None:
        # Create a basic Chart.yaml 
        chart_data = {
            'apiVersion': 'v2',
            'name': 'k8s-ctf-chart',
            'type': 'application',
            'description': 'Parent Chart for CTF challenges',
            'version': '0.1.0',
            'appVersion': '0.1.0',
            'dependencies': []
        }
    dependencies = chart_data.get('dependencies', [])
    
    # Create new dependency entry
    # Repository points to file://./charts, that is the subchart folder
    new_dependency = {
        'name': safe_name,
        'version': '0.1.0', 
        'repository': 'file://./charts',
        'condition': f'{safe_name}.enabled', 
        'alias': safe_name 
    }
    dependencies = [d for d in dependencies if d.get('name') != safe_name]
    dependencies.append(new_dependency)
    chart_data['dependencies'] = dependencies
    
    # Write the updated Chart.yaml
    write_chart_yaml(file_path, chart_data)
    return new_dependency