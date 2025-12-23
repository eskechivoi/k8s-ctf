import json
import subprocess
from flask import current_app as app, jsonify, request
from werkzeug.utils import secure_filename
from ..utils.helmUtils import install, uninstall, list_releases
from ..utils.k8sUtils import K8sChallengeDiscovery

def _get_release_name(challenge_name, user_id):
    safe_challenge_name = secure_filename(challenge_name).lower()
    return f"{secure_filename(user_id).lower()}-{safe_challenge_name}" 

def deploy_challenge_controller():
    """
    Performs a helm install of the parent chart, including enabled subcharts.
    ---
    tags:
      - Deployments
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
            - challenge_name
          properties:
            user_id:
              type: string
              example: "johndoe"
            challenge_name:
              type: string
              example: "ctfChallengeName"
    responses:
      200:
        description: Deployment successful.
        schema:
          properties:
            message: {type: string, example: "Deployment of 'ctfChallengeName' successful for user 'johndoe'."}
            release_name: {type: string, example: "johndoe-ctfChallengeName"}
      400:
        description: Missing required fields.
        schema:
          properties:
            error: {type: string, example: "Missing user_id or challenge_name."}
      408:
        description: Helm command timed out.
        schema:
          properties:
            error: {type: string"}
      500:
        description: |
          Internal server error. Possible scenarios:
          - Helm deployment failed.
          - Helm binary not found in system (FileNotFoundError)
        schema:
          type: object
          required:
            - error
          properties:
            error: {type: string}
            release_name: {type: string}
            helm_output: {type: string}
    """
    data = request.get_json()
    user_id = data.get('user_id')
    challenge_name = data.get('challenge_name')

    if not user_id or not challenge_name:
        return jsonify({"error": "Missing user_id or challenge_name."}), 400

    safe_challenge_name = secure_filename(challenge_name).lower()
    release_name = _get_release_name(challenge_name, user_id)
    parent_chart_path = app.config['PARENT_CHART_PATH']
    challenges_namespace = app.config['CHALLENGES_NAMESPACE']
    gateway_namespace = app.config['GATEWAY_API_NAMESPACE']
    
    # Enables subchart
    set_value = f'{safe_challenge_name}.enabled=true'
    
    try:
        result = install(
            release_name,
            parent_chart_path,
            set_value,
            challenges_namespace,
            gateway_namespace
        )
        app.logger.info(f"Executed: {' '.join(result.args)}")
        
        # If successful, returns helm install output
        return jsonify({
            "message": f"Deployment of '{challenge_name}' successful for user '{user_id}'.",
            "release_name": release_name,
        }), 200

    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error during Helm deployment: {e.stderr}")
        return jsonify({
            "error": "Helm deployment failed.",
            "helm_error": e.stderr.split('\n'),
            "command": ' '.join(e.cmd)
        }), 500
    except subprocess.TimeoutExpired:
        app.logger.error("Helm command timed out.")
        return jsonify({"error": "Helm command timed out."}), 408
    except FileNotFoundError:
        app.logger.error("'helm' command was not found. Make sure helm is installed in the system.")
        return jsonify({"error": "'helm' binary was not found."}), 500

def get_deployed_challenges_controller():
    """
    Retrieves the list of currently installed Helm releases (deployed challenges).
    ---
    tags:
      - Deployments
    parameters:
      - name: user_id
        in: query
        type: string
        required: false
        description: Optional filter to see only a specific user's challenges.
        example: "johndoe"
    responses:
      200:
        description: A list of deployed challenges.
        schema:
          type: array
          items:
            type: object
            properties:
              release_name: {type: string}
              chart: {type: string}
              revision: {type: string}
              status: {type: string}
              namespace: {type: string}
      408:
        description: Helm command timed out.
        schema:
          properties:
            error: {type: string"}
      500:
        description: |
          Internal server error. Possible scenarios:
          - Failed to parse Helm output. Raw output was not valid JSON.
          - Helm binary not found in system (FileNotFoundError)
        schema:
          type: object
          required:
            - error
          properties:
            error: {type: string}
            release_name: {type: string}
            helm_output: {type: string}
    """
    user_id = request.args.get('user_id')
    try:
        result = list_releases(app.config['CHALLENGES_NAMESPACE'])
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
            for r in releases
            if r.get('status') in ['deployed', 'pending-upgrade']
            and (not user_id or user_id in r.get('name', ''))
        ]
        return jsonify(deployed_challenges), 200
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error during Helm list: {e.stderr}")
        return jsonify({
            "error": "Helm list failed.",
            "helm_error": e.stderr.split('\n'),
            "command": ' '.join(e.cmd)
        }), 500
    except subprocess.TimeoutExpired:
        app.logger.error("Helm list command timed out.")
        return jsonify({"error": "Helm list command timed out."}), 408
    except FileNotFoundError:
        app.logger.error("'helm' command was not found. Make sure helm is installed in the system.")
        return jsonify({"error": "'helm' binary was not found."}), 500
    except json.JSONDecodeError:
        app.logger.error(f"Failed to decode JSON from helm output: {result.stdout}")
        return jsonify({"error": "Failed to parse Helm output. Raw output was not valid JSON."}), 500
    
def uninstall_challenge_controller():
    """
    Uninstalls the helm release for a user and a challenge.
    ---
    tags:
      - Deployments
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
            - challenge_name
          properties:
            user_id: {type: string, example: "johndoe"}
            challenge_name: {type: string, example: "ctfChallengeName"}
    responses:
      200:
        description: Challenge uninstalled successfully.
        schema:
          properties:
            message: {type: string}
            release_name: {type: string}
            helm_output: {type: array, items: {type: string}}
      400:
        description: Missing user_id or challenge_name.
        schema:
          type: object
          properties:
            error: {type: string}
      408:
        description: Helm command timed out.
        schema:
          type: object
          properties:
            error: {type: string}
      500:
        description: |
          Internal server error. Possible scenarios:
          - Helm uninstall command failed.
          - Helm binary not found in system (FileNotFoundError)
        schema:
          type: object
          required:
            - error
          properties:
            error: {type: string}
            release_name: {type: string}
            helm_output: {type: string}
    """
    data = request.get_json()
    user_id = data.get('user_id')
    challenge_name = data.get('challenge_name')

    if not user_id or not challenge_name:
        return jsonify({"error": "Missing user_id or challenge_name."}), 400

    release_name = _get_release_name(challenge_name, user_id)
    challenges_namespace = app.config['CHALLENGES_NAMESPACE']

    try:
        result = uninstall(release_name, challenges_namespace)
        app.logger.info(f"Executed: {' '.join(result.args)}")
        
        # If successful, returns helm install output
        return jsonify({
            "message": f"Successfully uninstalled challenge '{challenge_name}' for user '{user_id}'.",
            "release_name": release_name,
            "helm_output": result.stdout.split('\n')
        }), 200

    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error during Helm uninstall: {e.stderr}")
        return jsonify({
            "error": "Helm uninstall failed.",
            "helm_error": e.stderr.split('\n'),
            "command": ' '.join(e.cmd)
        }), 500
    except subprocess.TimeoutExpired:
        app.logger.error("Helm command timed out.")
        return jsonify({"error": "Helm command timed out."}), 408
    except FileNotFoundError:
        app.logger.error("'helm' command was not found. Make sure helm is installed in the system.")
        return jsonify({"error": "'helm' binary was not found."}), 500
    
def get_endpoint_for_challenge():
    """
    Returns the URL to access the challenge.
    ---
    tags:
      - Deployments
    parameters:
      - name: user_id
        in: query
        type: string
        required: true
        description: Name of the user.
        example: "johndoe"
      - name: challenge_name
        in: query
        type: string
        required: true
        description: Name of the challenge.
        example: "ctfChallengeName"
    responses:
      200:
        description: URL path to the challenge.
        schema:
          type: array
          items:
            type: object
            properties:
              "path": {type: string}
              "node_port": {type: string}
              "service": {type: string}
      400:
        description: Missing user_id or challenge_name
        schema:
          type: object
          properties:
            error: {type: string}
      404:
        description: HTTPRoute object not found for the challenge.
        schema:
          type: object
          properties:
            error: {type: string}
    """
    user_id = request.args.get('user_id')
    challenge_name = request.args.get('challenge_name')
    challenges_namespace = app.config['CHALLENGES_NAMESPACE']
    challenge_fullname = f"{user_id}-{challenge_name}"

    if not user_id or not challenge_name:
        return jsonify({"error": "Missing user_id or challenge_name."}), 400
    
    discovery = K8sChallengeDiscovery(namespace=challenges_namespace)
    data = discovery.get_endpoints(challenge_fullname)
    if data is None:
        return jsonify({"error": "Challenge route not found"}), 404
    return jsonify(data), 200