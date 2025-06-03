import mlflow.pyfunc
import numpy as np
import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset, ClassificationPreset
from evidently import Dataset, DataDefinition, BinaryClassification
from mlflow.models import set_model

import mlflow.pyfunc
import joblib
from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import REGISTRY
import logging

class SklearnModel(mlflow.pyfunc.PythonModel):
    def __init__(self):
        self.model = None
        self.server_started = False

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

        for metric in list(REGISTRY._collector_to_names):
            REGISTRY.unregister(metric)
        self._predict_counter = Gauge("model_predictions", "Number of predictions made")
        self._last_output_avg = Gauge("last_output_average", "Average of last predictions")
        self._vibration_drift = Gauge("vibration_drift", "Vibration drift")
        self._machineID_drift = Gauge("machineID_drift", "MachineID drift")
            
    def load_context(self, context):
        self.model = joblib.load(context.artifacts["model_path"])
        self.training_set = joblib.load(context.artifacts["trainig_path"])
    
    def predict(self, model_input:pd.DataFrame, params = None)->np.array:
        preds = self.model.predict(model_input)
        self._predict_counter.set(len(preds))
        self._last_output_avg.set(sum(preds) / len(preds))

        # Data drift
        rf_class_report = Report(metrics=[DataDriftPreset()])
        res = rf_class_report.run(reference_data=self.training_set, current_data=model_input)
        res = res.dict()
        self.logger.debug(f'Drift response: {res}')
        drift_metrics = res['metrics']
        for result in drift_metrics:
            self.logger.debug(f'Result: {result}')
            if 'machineID' in result['metric_id']:
                self._machineID_drift.set(result['value'])
            if 'vibration' in result['metric_id']:
                self._vibration_drift.set(result['value'])

        return preds
    
set_model(SklearnModel())
    