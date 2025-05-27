from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.http.operators.http import HttpOperator
import json

import pandas as pd
import random

data = pd.read_csv('/Data/test/x_test.csv')
data.columns = ['row', 'machineID', 'volt', 'rotate', 'pressure', 'vibration']
data = data.drop(columns='row')

index = random.sample(range(len(data)), 1)
test_data = data.iloc[index]
test_data

default_args = {
    'owner': 'ml_team',
    'depends_on_past': False,
    'retries': 4,
    'retry_delay': timedelta(seconds=30),
}

# Define the DAG (runs every minute)
with DAG(
    dag_id='mlflow_minute_predictions',
    default_args=default_args,
    schedule='0 0 * * *',  # Daily
    start_date=datetime(2025, 5, 26),
    catchup=False,
    tags=['mlflow', 'predictions'],
) as dag:

    # Task 1: Send prediction request to MLflow Docker container
    # Define your JSON data structure
    request_data = [
        {
            "machineID": 9,
            "volt": 165.6192236417,
            "rotate": 385.1685085587,
            "pressure": 99.154495789,
            "vibration": 33.6930473712
        }
    ]
    predict = HttpOperator(
        task_id='call_mlflow_model',
        method='POST',
        http_conn_id='RF_FAILURE_PREDICTOR',  # Configured in Airflow Connections,
        endpoint='/invocations',  # MLflow's default endpoint
        headers={"Content-Type": "application/json"},
        data=json.dumps(request_data),
        response_check=lambda response: response.status_code == 200,
        log_response=True,
    )

    # Task 2: Process the prediction (optional)
    def log_prediction(**kwargs):
        ti = kwargs['ti']
        prediction = json.loads(ti.xcom_pull(task_ids='call_mlflow_model'))
        print(f"Prediction result: {prediction}")
        # Could store in DB, send alert, etc.

    process_result = PythonOperator(
        task_id='process_prediction',
        python_callable=log_prediction
    )

    # Define task dependencies
    predict >> process_result
