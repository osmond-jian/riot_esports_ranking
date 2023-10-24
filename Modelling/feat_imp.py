import sagemaker
from sagemaker import Predictor
from sagemaker.serializers import CSVSerializer
from sagemaker import get_execution_role
import pandas as pd
import boto3
import botocore
import xgboost
import matplotlib.pyplot as plt

botocore.config.Config(signature_version=botocore.UNSIGNED, region_name='us-east-2')


# Initialize the predictor
endpoint_name = "lolpowerrank-model"

train_data = pd.read_csv("train_v4.csv")
test_data = pd.read_csv("test_v4.csv")
df = pd.concat([train_data,test_data],ignore_index=True)
#drop target

sagemaker_session = sagemaker.Session()
role = get_execution_role()
# role = 'arn:aws:iam::628064933526:role/service-role/AmazonSageMaker-ExecutionRole-20231023T123848'

sm = boto3.client('sagemaker')

automl_job_name = "lolpowerrank3"
description = sm.describe_auto_ml_job(AutoMLJobName=automl_job_name)

best_candidate = sm.describe_auto_ml_job(AutoMLJobName=automl_job_name)['BestCandidate']
best_candidate_name = best_candidate['CandidateName']

#!tar -xzvf model.tar.gz
# Load model
model = xgboost.Booster()
model.load_model('xgboost-model')  # Replace with the correct model artifact filename if different

# Get feature importance
feature_importance = model.get_score(importance_type='weight')

# Plot feature importance
xgboost.plot_importance(model, max_num_features=20)
plt.show()

# Mapping to original names
categorical_columns = train_data.select_dtypes(include=['object']).columns.tolist()

df_encoded = pd.get_dummies(train_data, drop_first=False, columns=categorical_columns)  # specify the categorical columns

mapping = {f"f_{i}": column for i, column in enumerate(df_encoded.columns)}