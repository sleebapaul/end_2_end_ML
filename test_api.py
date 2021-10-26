import json
import requests

features = ['bedrooms', 'bathrooms', 'sqft_living',
            'sqft_lot', 'floors', 'waterfront', 'view', 
            'condition', 'grade', 'sqft_above', 'sqft_basement']


inference_request = {
    "parameters": {
        "content_type": "pd"
    },
    "inputs": [
        {
          "name": "bedrooms",
          "shape": [1],
          "datatype": "FP32",
          "data": [3],
          "parameters": {
              "content_type": "np"
          }
        },
        {
          "name": "bathrooms",
          "shape": [1],
          "datatype": "FP32",
          "data": [1],
          "parameters": {
              "content_type": "np"
          }
        },
        {
          "name": "sqft_living",
          "shape": [1],
          "datatype": "FP32",
          "data": [1180],
          "parameters": {
              "content_type": "np"
          }
        },
        {
          "name": "sqft_lot",
          "shape": [1],
          "datatype": "FP32",
          "data": [5650],
          "parameters": {
              "content_type": "np"
          }
        },
        {
          "name": "floors",
          "shape": [1],
          "datatype": "FP32",
          "data": [1],
          "parameters": {
              "content_type": "np"
          }
        },
        {
          "name": "waterfront",
          "shape": [1],
          "datatype": "FP32",
          "data": [0],
          "parameters": {
              "content_type": "np"
          }
        },
        {
          "name": "view",
          "shape": [1],
          "datatype": "FP32",
          "data": [0],
          "parameters": {
              "content_type": "np"
          }
        },
        {
          "name": "condition",
          "shape": [1],
          "datatype": "FP32",
          "data": [3],
          "parameters": {
              "content_type": "np"
          }
        },
        {
          "name": "grade",
          "shape": [1],
          "datatype": "FP32",
          "data": [7],
          "parameters": {
              "content_type": "np"
          }
        },
        {
          "name": "sqft_above",
          "shape": [1],
          "datatype": "FP32",
          "data": [1180],
          "parameters": {
              "content_type": "np"
          }
        },
        {
          "name": "sqft_basement",
          "shape": [1],
          "datatype": "FP32",
          "data": [0],
          "parameters": {
              "content_type": "np"
          }
        },
    ]
}

# note is the local balancer for istion, make sure that the ip is reflected in the setup,
# run kubectl get service -n istio-system

endpoint = "http://localhost:8003/seldon/default/mlflow/v2/models/infer"
response = requests.post(endpoint, json=inference_request)

print(response.status_code)
print(json.dumps(response.json(), indent=2))
assert response.ok