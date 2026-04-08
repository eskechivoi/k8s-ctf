from CTFd.plugins import register_plugin_assets_directory
from CTFd.utils.plugins import register_script
from CTFd.plugins.ctfd_k8s_plugin.blueprint import k8s_bp
from CTFd.plugins.ctfd_k8s_plugin.extensions import limiter

def load(app):
    limiter.init_app(app)
    app.register_blueprint(k8s_bp)
    register_plugin_assets_directory(
        app, 
        base_path='/plugins/ctfd_k8s_plugin/assets/'
    )
    register_script('/plugins/ctfd_k8s_plugin/assets/navbar_injector.js')