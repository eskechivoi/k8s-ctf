import os

K8S_API_URL = os.getenv('K8S_CTF_API_URL', 'http://localhost:5000')
K8S_API_HOST = os.getenv('K8S_CTF_API_HOST', 'localhost')
K8S_API_HOST_INTERNAL = os.getenv('K8S_CTF_API_HOST', 'k8s-api.lan')