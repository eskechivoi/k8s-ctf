import subprocess

def update_dependencies(parent_chart_path):
    return subprocess.run(
        ['helm', 'dependency', 'update', '.'],
        capture_output=True,
        text=True,
        check=True,
        cwd=parent_chart_path
    )

def install(release_name, parent_chart_path, set_value, challenges_namespace):
    helm_command = [
        'helm', 'install',
        release_name,
        parent_chart_path,
        '--set', set_value,
        '--namespace', challenges_namespace
    ]
    return subprocess.run(
        helm_command,
        capture_output=True,
        text=True,
        check=True, 
        timeout=60
    )

def uninstall(release_name, challenges_namespace):
    helm_command = [
        'helm', 'uninstall',
        release_name,
        '--namespace', challenges_namespace
    ]
    return subprocess.run(
        helm_command,
        capture_output=True,
        text=True,
        check=True, 
        timeout=60
    )

def list_releases(challenges_namespace):
    """
    Executes 'helm list -o json' to get all installed releases in JSON format.
    The output is captured and returned for processing in the controller.
    """
    helm_command = [
        'helm', 'list',
        '-n', challenges_namespace,
        '--output', 'json'
    ]
    return subprocess.run(
        helm_command,
        capture_output=True,
        text=True,
        check=True, 
        timeout=30
    )