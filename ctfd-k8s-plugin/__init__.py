from flask import Blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from CTFd.plugins import register_plugin_assets_directory
from CTFd.utils.plugins import register_script
from CTFd.plugins.ctfd_k8s_plugin.blueprint import k8s_bp

limiter = Limiter(key_func=get_remote_address)

def load(app):
    limiter.init_app(app)
    app.register_blueprint(k8s_bp)
    register_plugin_assets_directory(
        app, 
        base_path='/plugins/ctfd_k8s_plugin/assets/'
    )
    register_script('/plugins/ctfd_k8s_plugin/assets/navbar_injector.js')