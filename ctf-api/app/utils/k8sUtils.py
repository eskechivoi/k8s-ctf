from kubernetes import client

class K8sChallengeDiscovery:
    def __init__(self, namespace="default"):        
        self.custom_api = client.CustomObjectsApi()
        self.v1 = client.CoreV1Api()
        self.namespace = namespace

        # Gateway API CDR
        self.group = "gateway.networking.k8s.io"
        self.version = "v1"
        self.plural = "httproutes"

    def get_endpoints(self, challenge_fullname):
        """
        Reads the HTTPRoute resource and maps every path with the port of its servicio.
        """
        route_name = f"{challenge_fullname}-route"
        results = []

        try:
            route = self.custom_api.get_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=self.namespace,
                plural=self.plural,
                name=route_name
            )
            rules = route.get('spec', {}).get('rules', [])
            for rule in rules:
                path = rule['matches'][0]['path']['value']
                backend_svc_name = rule['backendRefs'][0]['name']
                svc = self.v1.read_namespaced_service(backend_svc_name, self.namespace)
                node_port = svc.spec.ports[0].node_port
                results.append({
                    "path": path,
                    "node_port": node_port,
                    "service": backend_svc_name
                })
            return results
        except client.exceptions.ApiException as e:
            print(f"Error retrieving the challenge information: {e}")
            return None