import subprocess
from flask import current_app as app, jsonify, request
from werkzeug.utils import secure_filename
from ..utils.helmUtils import install, list_releases

def deploy_challenge_controller():
    """
    helm install of parent chart, enabling desired subchart.
    (POST /api/deployment)
    """
    data = request.get_json()
    user_name = data.get('user_name')
    challenge_name = data.get('challenge_name')

    if not user_name or not challenge_name:
        return jsonify({"error": "Missing user_name or challenge_name."}), 400

    release_name = secure_filename(user_name).lower()
    safe_challenge_name = secure_filename(challenge_name).lower()
    parent_chart_path = app.config['PARENT_CHART_PATH']
    
    # Enables subchart
    set_value = f'{safe_challenge_name}.enabled=true'
    
    try:
        result = install(release_name, parent_chart_path, set_value)
        app.logger.info(f"Executed: {' '.join(result.args)}")
        
        # If successful, returns helm install output
        return jsonify({
            "message": f"Deployment of '{challenge_name}' successful for user '{user_name}'.",
            "release_name": release_name,
            "helm_output": result.stdout.split('\n')
        }), 200

    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error during Helm deployment: {e.stderr}")
        return jsonify({
            "error": "Helm deployment failed.",
            "helm_error": e.stderr.split('\n'),
            "command": ' '.join(result.args)
        }), 500
    except subprocess.TimeoutExpired:
        app.logger.error("Helm command timed out.")
        return jsonify({"error": "Helm command timed out."}), 500
    except FileNotFoundError:
        app.logger.error("'helm' command was not found. Make sure helm is installed in the system.")
        return jsonify({"error": "'helm' binary was not found."}), 500

def get_deployed_challenges_controller():
    """
    Retrieves the list of currently installed Helm releases (deployed challenges).
    (GET /api/deployment)
    """
    try:
        result = list_releases()
        app.logger.info(f"Executed: {' '.join(result.args)}")
        output_str = result.stdout.strip()
        if not output_str:
            releases = []
        else:
            releases = json.loads(output_str)
        deployed_challenges = [
            {
                "release_name": r.get('name'),
                "chart": r.get('chart'),
                "revision": r.get('revision'),
                "status": r.get('status'),
                "namespace": r.get('namespace'),
            }
            for r in releases if r.get('status') in ['deployed', 'pending-upgrade']
        ]
        return jsonify({
            "message": f"Successfully retrieved {len(deployed_challenges)} deployed challenges.",
            "challenges": deployed_challenges
        }), 200
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error during Helm list: {e.stderr}")
        return jsonify({
            "error": "Helm list failed.",
            "helm_error": e.stderr.split('\n'),
            "command": ' '.join(e.cmd)
        }), 500
    except subprocess.TimeoutExpired:
        app.logger.error("Helm list command timed out.")
        return jsonify({"error": "Helm list command timed out."}), 500
    except FileNotFoundError:
        app.logger.error("'helm' command was not found. Make sure helm is installed in the system.")
        return jsonify({"error": "'helm' binary was not found."}), 500
    except json.JSONDecodeError:
        app.logger.error(f"Failed to decode JSON from helm output: {result.stdout}")
        return jsonify({"error": "Failed to parse Helm output. Raw output was not valid JSON."}), 500