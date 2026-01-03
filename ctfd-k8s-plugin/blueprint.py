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
    user = get_current_user()
    k8s_user_id = _get_user_id(user)
    active_tab = request.args.get('tab', 'available')
    
    available_challenges = []
    my_deployments = []
    headers = {"Host": K8S_API_HOST, "Accept": "application/json"}

    if active_tab == 'available':
        try:
            resp = requests.get(f"{K8S_API_URL}/dependencies", headers=headers, timeout=5)
            if resp.status_code == 200:
                available_challenges = resp.json()
        except Exception as e:
            flash(f"Error loading challenges: {e}", "danger")

    elif active_tab == 'deployed':
        try:
            resp = requests.get(f"{K8S_API_URL}/deployment", params={'user_id': k8s_user_id}, headers=headers, timeout=5)
            if resp.status_code == 200:
                my_deployments = resp.json() if isinstance(resp.json(), list) else []                
                for dep in my_deployments:
                    release = dep.get('release_name', '')
                    challenge_name = release.split('-', 1)[1] if '-' in release else release
                    dep['challenge_name'] = challenge_name
                    try:
                        ep_resp = requests.get(
                            f"{K8S_API_URL}/deployment/endpoint", 
                            params={'user_id': k8s_user_id, 'challenge_name': challenge_name},
                            headers=headers, timeout=5
                        )
                        if ep_resp.status_code == 200:
                            data = ep_resp.json()
                            dep['connection_info'] = data if isinstance(data, list) else [data]
                    except:
                        pass
        except Exception as e:
            flash("Error loading deployments.", "danger")

    return render_template(
        'k8s_dashboard.html', 
        available=available_challenges, 
        deployed=my_deployments,
        host=K8S_API_HOST,
        active_tab=active_tab
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