# End to End ML Pipeline with MLflow and Seldon Core

This README depicts a CLI setup guide in Macbook (M1). Things might look different in other platform, but order of setup would be the same. 

### Reproducable experimentation 

First and foremost step is setting up a reproducable ML experimentation system. For that we need, 

1. An ML experiment tracking system - <font color='green'>MLflow</font>
2. A database to store the experimentation tracking system data - <font color='green'> MySQL DB</font>
3. A local object store to keep the artifacts of each experiment -  <font color='green'>MinIO</font>

![Training Flow Chart](/images/mlflow_train.png "seldon training")

Here we are setting everything using dockers, so all three above can be actualized as containers. In the `experiments` folder, we have a `Dockerfile` which will setup a container that has

1. Training script 
2. Training data 

There are provisions to add test scripts, if required. 

Another aspect is, the training data is added as a file. In a real setup, it won't be the case. The training data could be streaming data, or stored in a DB or anything. 

- Install Docker for Desktop
- Start from clean slate
    - `docker-compose down`
    - `docker system prune --force --volumes`

- `docker-compose --env-file ./.env up`

This command should give, 

1. Mlflow dashboard at `localhost:5000` 
2. MinIO dashboard at `localhost:9000`

Run the training script available in `experiments` folder to simualate the training in MLflow. 

```bash
cd experiments 
python3 train.py
```

You can see the experiments in `localhost:5000`, metrics and the artifacts in `localhost:9000`. This is configured in the `train.py`. If you want to run locally, edit the script.

### Deployment in Kubernates

Once we've the trained models which meets the metric criterias, we can deploy it.

Seldon, is an MLOps framework, to package, deploy, monitor and manage thousands of production ML models 

`SeldonDeployment CRD` makes many things easy by doing an abstraction over the entire inference pipeline. Some important features are,

- There are pre-built servers available for subset of ML frameworks. Eg. `Scikit-Learn`.

- A/B Testings, Shadow deployments etc. 

- Integration with explainability, outlier detection frameworks 

- Integration with monitoring, logging, scaling etc. 

- Seldon Core is a cloud native solution built heavily on Kubernates APIs makes it easy for Seldon to run on any cloud provider. On premise providers are also supported. 

![Seldon Core Block Diagram](/images/seldon_core.jpeg "seldon core")

There are some issues going on with latest kubernetes version and Seldon Core. [Follow this thread for the details.](https://github.com/SeldonIO/seldon-core/issues/3618). I used Docker Desktop with used Kubernetes 1.21.5. 

- Install Docker Desktop.
- Enable Kubernetes in the settings. 
- Install Helm `brew install helm` 
- Install Seldon Core, Ambassodor,  Seldon Analytics with Prometheus and Grafana 
    ```bash 
    kubectl create namespace ambassador || echo "namespace ambassador exists"

    helm repo add datawire https://www.getambassador.io

    helm install ambassador datawire/ambassador --set image.repository=docker.io/datawire/ambassador --set crds.keep=false --namespace ambassador

    kubectl create namespace seldon-system
    
    helm install seldon-core seldon-core-operator --repo https://storage.googleapis.com/seldon-charts --set istio.enabled=true --set usageMetrics.enabled=true --namespace seldon-system

    helm install seldon-core-analytics seldon-core-analytics --namespace seldon-system --repo https://storage.googleapis.com/seldon-charts --set grafana.adminPassword=password --set grafana.adminUser=admin
    ```
- Setup the `kubernetes-dashboard` if you would like to, from [here.](https://andrewlock.net/running-kubernetes-and-the-dashboard-with-docker-desktop/)
    - `http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/`
- Create deployment 
    ```bash
    kubectl get deploy -n seldon-system
    ```
        
    This should give the following response. 

    ```
    NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
    seldon-controller-manager   1/1     1            1           93s
    ```
- You may check the Ambassodor pods as well using `kubectl get po -n ambassador`

- Setup MinIO 
    ```bash
    kubectl create ns minio-system 
    
    helm repo add minio https://helm.min.io/
    helm install minio minio/minio --set accessKey=minioadmin \
    --set secretKey=minioadmin --namespace minio-system
    ```

- Follow the steps in the trace.
    ```bash
    kubectl get secret $(kubectl get serviceaccount console-sa --namespace minio-system -o jsonpath="{.secrets[0].name}") --namespace minio-system -o jsonpath="{.data.token}" | base64 --decode

    kubectl rollout status deployment -n minio-system minio-operator
    ```

- On another terminal, 
    ```bash

    export POD_NAME=$(kubectl get pods --namespace minio-system -l "release=minio" -o jsonpath="{.items[0].metadata.name}")

    kubectl port-forward $POD_NAME 9000 --namespace minio-system
    ```
- Configure the MinIO client and copy the models 

    ```bash
    mc config host add minio-local http://localhost:9000 minioadmin minioadmin

    mc mb minio-local/mlflow
    mc cp experiments/buckets/mlflow/0/<experiment-id>/artifacts/rf-regressor minio-local/mlflow/
    ```
- Apply the deployment settings

    ```bash
    kubectl apply -f secret.yaml
    kubectl apply -f deploy.yaml

    kubectl rollout status deploy/$(kubectl get deploy -l seldon-deployment-id=minio-sklearn -o jsonpath='{.items[0].metadata.name}')
    ```

4. Delete the deployment and pods

    ```bash 
    kubectl delete -f deploy.yaml
    kubectl delete -f secret.yaml
    kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.2.0/aio/deploy/recommended.yaml
    ```

Reference 

[1] [Alejandro Saucedo's Medium article](https://towardsdatascience.com/a-simple-mlops-pipeline-on-your-local-machine-db9326addf31)

[2] [Adrian Gonzalez's PPT](https://docs.google.com/presentation/d/1QXiOZkd_XNw6PbUalhYDajljKYQjgKczzNncTyLk9uA/)

[3] [Adrian Gonzalez's Talk](https://www.youtube.com/watch?v=M_q0-8JH0Zw)

[4] [A Simple MLOps Pipeline on Your Local Machine](https://towardsdatascience.com/a-simple-mlops-pipeline-on-your-local-machine-db9326addf31)

[5] [MLflow On-Premise Deployment - GitHub](https://github.com/sachua/mlflow-docker-compose)

[6] [SKlearn Prepackaged Server with MinIO](https://docs.seldon.io/projects/seldon-core/en/v1.1.0/examples/minio-sklearn.html)

[7] [Install MinIO in cluster](https://docs.seldon.io/projects/seldon-core/en/latest/examples/minio_setup.html)

