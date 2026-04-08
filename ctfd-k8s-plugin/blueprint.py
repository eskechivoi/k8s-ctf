import requests
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from CTFd.plugins.ctfd_k8s_plugin.extensions import limiter
from CTFd.utils.dates import ctf_has_started
from CTFd.utils.decorators import authed_only
from CTFd.utils.user import get_current_user, is_admin
from CTFd.plugins.ctfd_k8s_plugin.config import K8S_API_URL, K8S_API_HOST, K8S_API_LOAD_BALANCER, K8S_API_HOST_INTERNAL

k8s_bp = Blueprint('k8s_challenges', __name__, template_folder='templates', url_prefix='/k8s')

GENERIC_CONNECTION_ERROR = "Connection error to the Kubernetes CTF API. Please contact a CTFd admin."

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

    if not ctf_has_started() and not is_admin():
        available_challenges = [] 
        flash("The CTF event has not yet started.", "info")

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
        host=K8S_API_LOAD_BALANCER,
        host_internal=K8S_API_HOST_INTERNAL,
        active_tab=active_tab
    )

@k8s_bp.route('/deploy', methods=['POST'])
@authed_only
@limiter.limit(
    "3 per minute",
    error_message="You have exceeded the maximum number of challenges that can be deployed per minute (3)."
)
def deploy_challenge():
    if not ctf_has_started() and not is_admin():
        return jsonify({"error": "The CTF event has not yet started."}), 403

    user = get_current_user()
    challenge_name = request.form.get('challenge_name')
    if not challenge_name:
        flash("Internal error while trying to deploy the challenge.", "warning")
        print("Challenge name is missing when trying to deploy the challenge!")
        return redirect(url_for('k8s_challenges.dashboard', tab='available'))
    payload = {
        'user_id': _get_user_id(user),
        'challenge_name': challenge_name
    }
    headers = {
        "Host": K8S_API_HOST,
        "Accept": "application/json"
    }
    try:
        resp = requests.post(
            f"{K8S_API_URL}/deployment", 
            json=payload, 
            headers=headers, 
            timeout=45 
        )        
        try:
            data = resp.json()
        except ValueError:
            data = {}
        if resp.status_code == 200:
            msg = data.get('message', f"Challenge '{challenge_name}' deployment started!")
            flash(msg, "success")
        else:
            error_msg = data.get('error', f"Error {resp.status_code}: {resp.text[:100]}")
            flash(f"Failed to deploy: {error_msg}", "danger")
    except requests.exceptions.Timeout:
        flash("The deployment is taking too long, but it might still be processing in the background. Check 'My Deployments' in a minute.", "warning")
    except Exception as e:
        flash(GENERIC_CONNECTION_ERROR, "danger")
        app.logger.error(e)
    return redirect(url_for('k8s_challenges.dashboard', tab='deployed'))

@k8s_bp.route('/terminate', methods=['POST'])
@authed_only
@limiter.limit(
    "3 per minute",
    error_message="You have exceeded the maximum number of challenges that can be terminated per minute (3)."
)
def terminate_challenge():
    if not ctf_has_started() and not is_admin():
        return jsonify({"error": "The CTF event has not yet started."}), 403
    
    user = get_current_user()
    release_name = request.form.get('challenge_name') 
    payload = {
        'user_id': _get_user_id(user),
        'challenge_name': release_name
    }
    headers = {"Host": K8S_API_HOST}
    try:
        resp = requests.delete(f"{K8S_API_URL}/deployment", json=payload, headers=headers, timeout=30)        
        try:
            data = resp.json()
        except ValueError:
            data = {}
        if resp.status_code == 200:
            msg = data.get('message', 'Terminated successfully')
            flash(f"Success: {msg}", "success")
        else:
            error_msg = data.get('error', f"API Error (Status {resp.status_code})")
            flash(f"Failed to terminate: {error_msg}", "danger")
    except Exception as e:
        flash(GENERIC_CONNECTION_ERROR, "danger")
        app.logger.error(e)
    return redirect(url_for('k8s_challenges.dashboard', tab='deployed'))

@k8s_bp.errorhandler(429)
def ratelimit_handler(e):
    message = e.description if e.description else "Maximum number of requests per minute to the API exceeded (max. is 3)."
    flash(message, "danger")
    return redirect(url_for('k8s_challenges.dashboard'))