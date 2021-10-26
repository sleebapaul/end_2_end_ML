import os

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://localhost:9000"
os.environ['AWS_ACCESS_KEY_ID'] = "minio"
os.environ['AWS_SECRET_ACCESS_KEY'] = "minio123"

mlflow.set_tracking_uri("http://localhost:5000")
df = pd.read_csv("kc_house_data.csv") 

# choose features
features = ['bedrooms', 'bathrooms', 'sqft_living',
            'sqft_lot', 'floors', 'waterfront', 'view', 
            'condition', 'grade', 'sqft_above', 'sqft_basement']

# getting those features from the dataframe
x = df[features]
y = df["price"]

# splits data into 80% train 20% test
x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.7, 
                                                    random_state=3)

# choose model with settings
model = RandomForestRegressor(n_estimators=100) 
model.fit(x_train, y_train)

# define and print
metrics = {"train_score": model.score(x_train, y_train), 
"test_score": model.score(x_test, y_test)}
print(metrics)

# log params to mlflow and artifacts to minio
mlflow.log_params({"n_estimators":100})
mlflow.log_metrics(metrics)
mlflow.sklearn.log_model(model, "rf-regressor")
