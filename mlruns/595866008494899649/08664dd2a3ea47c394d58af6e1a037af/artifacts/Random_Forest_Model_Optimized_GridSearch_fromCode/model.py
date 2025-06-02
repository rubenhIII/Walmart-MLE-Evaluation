import mlflow.pyfunc
import numpy as np
import pandas as pd
from prometheus_client import Counter, Histogram, Gauge
from evidently import Report
from evidently.presets import DataDriftPreset, ClassificationPreset
from evidently import Dataset, DataDefinition, BinaryClassification
from mlflow.models import set_model

import socket
import mlflow.pyfunc
import joblib
from prometheus_client import start_http_server, Gauge
import threading
from prometheus_client import REGISTRY

class SklearnModel(mlflow.pyfunc.PythonModel):
    def __init__(self):
        self.model = None
        self.server_started = False

        for metric in list(REGISTRY._collector_to_names):
            REGISTRY.unregister(metric)
        self._predict_counter = Gauge("model_predictions", "Number of predictions made")
        self._last_output_avg = Gauge("last_output_average", "Average of last predictions")

    #def _start_prometheus(self):
    #   if not self.server_started:
    #        self.server_started = True
            # Define Prometheus metrics
            

    def load_context(self, context):
        self.model = joblib.load(context.artifacts["model_path"])
        #self._start_prometheus()
    
    def predict(self, model_input:pd.DataFrame, params = None)->np.array:
        preds = self.model.predict(model_input)
        self._predict_counter.set(len(preds))
        self._last_output_avg.set(sum(preds) / len(preds))
        return preds
    
set_model(SklearnModel())
    