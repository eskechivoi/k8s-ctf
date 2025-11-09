# k8s-ctf
Frontend, API and helm charts to easily deploy CTF challenges on kubernetes.

## ctf-api
Offers some endpoints to update the CTF challenges' charts and deploy a new challenge for a CTF player.
The `challenge-commons` chart is mounted as a volume in the `ctf-api` Pod. The new dependencies are added to this mounted volume by the API. An init container is in charge of downloading the `challenge-commons` chart from GitHub and adding it to the mounted volume.

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
- `challenge-commons` : Is the 'parent chart' for the challenges. It is mounted on the API Pod.
    - Defines the Ingress rules for the challenges.
    - Defines global values for the challenges' charts.
- `k8s-ctf-chart` : It is the 'parent chart' for the backend and the frontend Pods. 
    - Defines the Ingress rules to access the backend and the frontend.
    - Defines global values like replicas, labels...
- `challenge-chart-template` : To create a new chart for a challenge you can use this template.
- API chart : Deployment and service for the backend.
- Frontend chart: Deployment and service for the frontend.

## Install

First of all, you will need to have the ctf-api and ctf-frontend images build and accessible from within your Kubernetes cluster.
Assumming you're using a local setup like minikube, just build the images locally.

Once you have the images accesible from your cluster, run the following command:

```sh
helm dependency build
helm install k8s-ctf k8s-ctf-chart \
  --namespace k8sctf \
  --create-namespace
```

This will create the k8sctf namespace and install both the API and the frontend in that namespace.