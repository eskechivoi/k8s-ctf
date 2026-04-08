import time
import requests
from flask import flash, current_app
from CTFd.utils import get_config
from CTFd.plugins.ctfd_k8s_plugin.config import K8S_API_URL, K8S_API_HOST

GENERIC_CONNECTION_ERROR = "Connection error to the Kubernetes CTF API. Please contact a CTFd admin."

ACTION_FAILED_MSGS={
    'POST': "Failed to deploy",
    'DELETE': "Failed to terminate"
}
ACTION_SUCCESS_MSGS={
    'POST': "deployment started!",
    'DELETE': "terminated successfully."
}

def _get_user_id(user):
    return f"user{user.id}"

def ctf_has_started():
    start = get_config("start")
    if start:
        try:
            return int(start) < int(time.time())
        except (ValueError, TypeError):
            return True
    return True

def call_k8s_api(endpoint, method='GET', json_data=None, headers=None, params=None, timeout=45):
    try:
        resp = requests.request(
            method=method,
            url=f"{K8S_API_URL}/{endpoint}", 
            json=json_data, 
            headers=headers, 
            params=params,
            timeout=timeout
        )        

        try:
            data = resp.json()
        except ValueError:
            data = {}

        if resp.status_code == 200:
            challenge_name = json_data.get('challenge_name') if json_data else None
            if challenge_name:
                msg = f"Challenge '{challenge_name}' {ACTION_SUCCESS_MSGS.get(method, 'processed successfully')}."
            else:
                msg = f"Action {ACTION_SUCCESS_MSGS.get(method, 'completed')}."
            flash(msg, "success")
        else:
            error_msg = data.get('error', f"Error {resp.status_code}: {resp.text[:100]}")
            flash(f"{ACTION_FAILED_MSGS.get(method, 'Action failed')}: {error_msg}", "danger")
            
    except requests.exceptions.Timeout:
        flash("The deployment is taking too long, but it might still be processing in the background.", "warning")
    except Exception as e:
        flash(GENERIC_CONNECTION_ERROR, "danger")
        current_app.logger.error(f"K8S Plugin Error: {e}")