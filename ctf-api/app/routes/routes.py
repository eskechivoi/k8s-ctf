from flask import Blueprint
from ..controllers.dependenciesController import get_dependencies_controller, add_dependency_controller
from ..controllers.deploymentController import (
    deploy_challenge_controller,
    get_deployed_challenges_controller,
    uninstall_challenge_controller,
    get_endpoint_for_challenge
)

api_bp = Blueprint('api', __name__)

# Al asignar la función directamente, Flask mantiene el __doc__ original
api_bp.add_url_rule('/dependencies', view_func=get_dependencies_controller, methods=['GET'])
api_bp.add_url_rule('/dependencies', view_func=add_dependency_controller, methods=['POST'])

api_bp.add_url_rule('/deployment', view_func=get_deployed_challenges_controller, methods=['GET'])
api_bp.add_url_rule('/deployment', view_func=deploy_challenge_controller, methods=['POST'])
api_bp.add_url_rule('/deployment', view_func=uninstall_challenge_controller, methods=['DELETE'])
api_bp.add_url_rule('/deployment/endpoint', view_func=get_endpoint_for_challenge, methods=['GET'])