# k8s-ctf
Frontend, API and helm charts to easily deploy CTF challenges on kubernetes.

## k8s-ctf-api
Offers some endpoints to update the CTF challenges' charts and deploy a new challenge for a CTF player.
The `k8s-ctf-chart` is mounted as a volume in the `k8s-ctf-api` Pod. The new dependencies are added to this mounted volume by the API.
To make the dependency changes persistent, this 'parent chart' is uploaded to a PVC that is mounted on the API's Pod.

### Endpoints:
- /api/dependencies 
    - GET : Returns all the challenge charts installed in the cluster.
    - POST : Installs a new challenge in the cluster.
        - challenge_name: str, chart_file: file (in .tar format) - (as application/json)

- /api/deploy
    - POST: Deploys a new challenge for the user.
        - user_name: str, challenge_name: str (as application/json)