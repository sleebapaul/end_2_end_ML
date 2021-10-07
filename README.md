# End to End ML Pipeline with MLflow and Seldon Core

This README depicts a CLI setup guide in Macbook. Things might look different in other platform, but order of setup would be the same. 

1. Setup MLFlow for reproducable experimentation 

- Install `virtualengwrapper` and create new env `mkvirtualenv end_2_end_ml` 
- Install `mlflow` and `scikit-learn` 
    - `~/.virtualenvs/end_2_end_ml/bin/pip install mlflow scikit-learn`
- Run a couple of experiments with `train.py`
    - `~/.virtualenvs/end_2_end_ml/bin/python wine_data/train.py 0.5 0.2`
    - `~/.virtualenvs/end_2_end_ml/bin/python wine_data/train.py`
- Check the dashboard in MLFlow UI using `mlflow ui` command

OR 

Just install `MLFLow` and `conda` and run `mlflow run wine_data -P alpha=0.42`

Now we've the models trained, (ignore the performance as of now), these models can be served using MLFlow itself. 
For this project, I use Seldon.

Seldon, is an MLOps framework, to package, deploy, monitor and manage thousands of production ML models 

`SeldonDeployment CRD` makes many things easy by doing an abstraction over the entire inference pipeline. Some important features are,

- There are pre-built servers available for subset of ML frameworks. Eg. `Scikit-Learn`. Here I used `ElasticNet` from `Scikit-Learn`.

- A/B Testings, Shadow deployments etc. 

- Integration with explainability, outlier detection frameworks 

- Integration with monitoring, logging, scaling etc. 

- Seldon Core is a cloud native solution built heavily on Kubernates APIs makes it easy for Seldon to run on any cloud provider. On premise providers are also supported. 

![Seldon Core Block Diagram](/images/seldon_core.jpeg "seldon core")

2. Install Seldon Core 

There are some issues going on with latest kubernetes version and Seldon Core. [Follow this thread for the details.](https://github.com/SeldonIO/seldon-core/issues/3618). I used Docker Desktop with used Kubernetes 1.21.5. 

- Install Docker Desktop.
- Enable Kubernetes in the settings. 
- Install Helm `brew install helm` 
- Install Seldon Core, Seldon Analytics with Prometheus and Grafana 
- Install Seldon Core and Ambassodor
    - `kubectl create namespace ambassador || echo "namespace ambassador exists"` 
    - `helm repo add datawire https://www.getambassador.io`
    - `helm install ambassador datawire/ambassador --set image.repository=docker.io/datawire/ambassador --set crds.keep=false --namespace ambassador`
    - `kubectl create namespace seldon-system`
    - `helm install seldon-core seldon-core-operator --repo https://storage.googleapis.com/seldon-charts --set istio.enabled=true --set usageMetrics.enabled=true --namespace seldon-system`
    - `helm install seldon-core-analytics seldon-core-analytics --namespace seldon-system --repo https://storage.googleapis.com/seldon-charts --set grafana.adminPassword=password --set grafana.adminUser=admin`
    - `kubectl get deploy -n seldon-system`
        
        This should give the following response. 

        ```
        NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
        seldon-controller-manager   1/1     1            1           93s
        ```
- You may check the Ambassodor pods as well using `kubectl get po -n ambassador` 


3. Training Flowchart 

![Training Flow Chart](/images/training.png "seldon training")


Since I'm setting up everything offline, the model artifacts during various MLflow runs are moved to another folder. This folder path is required to be mentioned in the deployment script. You may give use the same `mlruns` folder path, I doing this additional step just to follow the standard process.

```
mkdir seldon-models
mkdir seldon-models/mlflow
mkdir seldon-models/mlflow
mkdir seldon-models/mlflow/model-a
mkdir seldon-models/mlflow/model-b

cp -r mlruns/0/64f15255a6614f73b71189a906459a10/artifacts/model/* seldon-models/mlflow/model-a
cp -r mlruns/0/e7a11ef4b6284409a9c65fb6c691e65b/artifacts/model/* seldon-models/mlflow/model-b
```

4. Deploy the trained models in the pods 

-  `kubectl create -f ./serving/model-a-b.yaml` (Imperative, creates a whole new object (previously non-existing / deleted))
- `kubectl apply -f ./serving/model-a-b.yaml` (Declarative, makes incremental changes to an existing object)

5. Delete the deployment and pods

- `kubectl delete -f ./serving/model-a-b.yaml`


Reference 

[1] [Alejandro Saucedo's Medium article](https://towardsdatascience.com/a-simple-mlops-pipeline-on-your-local-machine-db9326addf31)

[2] [Adrian Gonzalez's PPT](https://docs.google.com/presentation/d/1QXiOZkd_XNw6PbUalhYDajljKYQjgKczzNncTyLk9uA/)

[3] [Adrian Gonzalez's Talk](https://www.youtube.com/watch?v=M_q0-8JH0Zw)

