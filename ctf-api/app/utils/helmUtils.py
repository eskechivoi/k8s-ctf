import subprocess

def update_dependencies(parent_chart_path):
    return subprocess.run(
        ['helm', 'dependency', 'update', parent_chart_path],
        capture_output=True, text=True, check=True
    )

def install(release_name, parent_chart_path, set_value):
    helm_command = [
        'helm', 'install',
        release_name,
        parent_chart_path,
        '--set', set_value
    ]
    return subprocess.run(
        helm_command,
        capture_output=True,
        text=True,
        check=True, 
        timeout=60
    )

def list_releases():
    """
    Executes 'helm list -o json' to get all installed releases in JSON format.
    The output is captured and returned for processing in the controller.
    """
    helm_command = [
        'helm', 'list',
        '--all',
        '--output', 'json'
    ]
    return subprocess.run(
        helm_command,
        capture_output=True,
        text=True,
        check=True, 
        timeout=30
    )