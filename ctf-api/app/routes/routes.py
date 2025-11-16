from flask import Blueprint
from ..controllers.dependenciesController import get_dependencies_controller, add_dependency_controller
from ..controllers.deploymentController import deploy_challenge_controller, get_deployed_challenges_controller, uninstall_challenge_controller

api_bp = Blueprint('api', __name__)

# Endpoint for /api/dependencies (GET and POST)
api_bp.route('/dependencies', methods=['GET'])(get_dependencies_controller)
api_bp.route('/dependencies', methods=['POST'])(add_dependency_controller)

# Endpoint for /api/deployment (GET and POST)
api_bp.route('/deployment', methods=['GET'])(get_deployed_challenges_controller)
api_bp.route('/deployment', methods=['POST'])(deploy_challenge_controller)
api_bp.route('/deployment', methods=['DELETE'])(uninstall_challenge_controller)