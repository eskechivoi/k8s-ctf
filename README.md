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

## A lot of charts, init?
Well, every chart folder has it's own role in this whole architecture:
- `k8s-ctf-chart` : Is the 'parent chart' for the challenges. It is mounted to the API Pod.
    - Defines the Ingress rules for the challenges.
    - Defines global values for the challenges' charts.
- `k8s-parent-chart` : It is the 'parent chart' for the backend Pod and the frontend. 
    - Defines the Ingress rules to access the backend and the frontend.
    - Defines global values like replicas, labels...
- `challenge-chart-template` : To create a new chart for a challenge you can use this template.
- API chart : Deployment and service for the backend.
- Frontend chart: Deployment and service for the frontend.