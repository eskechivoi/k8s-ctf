import requests
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from CTFd.utils.decorators import authed_only
from CTFd.utils.user import get_current_user
from CTFd.plugins.ctfd_k8s_plugin.config import K8S_API_URL, K8S_API_HOST

k8s_bp = Blueprint('k8s_challenges', __name__, template_folder='templates', url_prefix='/k8s')

def _get_user_id(user):
    return f"user{user.id}"

@k8s_bp.route('/dashboard', methods=['GET'])
@authed_only
def dashboard():
    print("\n" + "="*20)
    print("Reloading bashboard!")
    print("="*20 + "\n")
    
    user = get_current_user()
    k8s_user_id = _get_user_id(user)
    available_challenges = []
    my_deployments = []
    headers = {
        "Host": K8S_API_HOST,
        "Accept": "application/json"
    }
    print(f"Checking API for user: {k8s_user_id}")
    try:
        print(f"Requesting: {K8S_API_URL}/dependencies")
        resp = requests.get(f"{K8S_API_URL}/dependencies", headers=headers, timeout=5)
        print(f"API HTTP Response Code: {resp.status_code}")
        if resp.status_code == 200:
            available_challenges = resp.json()
            print(f"Challenges received: {available_challenges}")
        elif resp.status_code >= 400:
            flash(f"Error trying to load the CTF challenges. Status code: {resp.status_code}", "danger")
    except Exception as e:
        flash(f"Error loading the CTF challenges: {e}", "danger")
    try:
        resp = requests.get(
            f"{K8S_API_URL}/deployment",
            params={'user_id': k8s_user_id},
            headers=headers,
            timeout=5
        )
        if resp.status_code == 200:
            data_deploy = resp.json()
            my_deployments = data_deploy if isinstance(data_deploy, list) else []
            
            for dep in my_deployments:
                dep['connection_info'] = {}                 
                release = dep.get('release_name', '')
                challenge_name = release.split('-', 1)[1] if '-' in release else release
                dep['challenge_name'] = challenge_name
                print(f"Checking endpoints for: {challenge_name}")
                try:
                    ep_resp = requests.get(
                        f"{K8S_API_URL}/deployment/endpoint", 
                        params={'user_id': k8s_user_id, 'challenge_name': challenge_name},
                        headers=headers,
                        timeout=5
                    )
                    print(ep_resp.json())
                    if ep_resp.status_code == 200:
                        ep_data = ep_resp.json()
                        if isinstance(ep_data, list):
                            dep['connection_info'] = ep_data
                        elif isinstance(ep_data, dict):
                            dep['connection_info'] = [ep_data]
                except Exception as e:
                    print(f"DEBUG: Silent error for endpoint {challenge_name}: {e}")
    except Exception as e:
        print(f"DEBUG: Critical failure retrieving deployments: {e}")
        flash("Error trying to obtain your active deployments.", "danger")

    return render_template(
        'k8s_dashboard.html', 
        available=available_challenges, 
        deployed=my_deployments,
        host=K8S_API_HOST
    )

@k8s_bp.route('/deploy', methods=['POST'])
@authed_only
def deploy_challenge():
    user = get_current_user()
    challenge_name = request.form.get('challenge_name')
    if not challenge_name:
        flash("Challenge name is missing.", "warning")
        return redirect(url_for('k8s_challenges.dashboard'))
    payload = {
        'user_id': _get_user_id(user),
        'challenge_name': challenge_name
    }
    try:
        resp = requests.post(f"{K8S_API_URL}/deployment", json=payload, timeout=30)
        if resp.status_code == 200:
            flash(f"Challenge '{challenge_name}' deployment started!", "success")
        else:
            error_msg = resp.json().get('error', 'Unknown error')
            flash(f"Failed to deploy: {error_msg}", "danger")
    except Exception as e:
        flash(f"Connection error: {e}", "danger")
    return redirect(url_for('k8s_challenges.dashboard'))

@k8s_bp.route('/terminate', methods=['POST'])
@authed_only
def terminate_challenge():
    user = get_current_user()
    challenge_name = request.form.get('challenge_name')
    payload = {
        'user_id': _get_user_id(user),
        'challenge_name': challenge_name
    }
    try:
        resp = requests.delete(f"{K8S_API_URL}/deployment", json=payload, timeout=30)
        if resp.status_code == 200:
            flash(f"Challenge '{challenge_name}' terminated successfully.", "success")
        else:
            error_msg = resp.json().get('error', 'Unknown error')
            flash(f"Failed to terminate: {error_msg}", "danger")
    except Exception as e:
        flash(f"Connection error: {e}", "danger")
    return redirect(url_for('k8s_challenges.dashboard'))