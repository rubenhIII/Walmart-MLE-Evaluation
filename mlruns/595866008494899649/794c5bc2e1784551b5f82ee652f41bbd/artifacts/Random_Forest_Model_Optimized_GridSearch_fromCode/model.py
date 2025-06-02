import mlflow.pyfunc
import numpy as np
import pandas as pd
from prometheus_client import Counter, Histogram, Gauge
from evidently import Report
from evidently.presets import DataDriftPreset, ClassificationPreset
from evidently import Dataset, DataDefinition, BinaryClassification
from mlflow.models import set_model

from sklearn.ensemble import RandomForestClassifier

class SklearnModel(mlflow.pyfunc.PythonModel):
    def __init__(self):
        rdmf = RandomForestClassifier(criterion='entropy', max_depth=5, max_features=None)
        x_train = pd.read_csv('Data/training/x_train.csv')
        y_train = pd.read_csv('Data/training/y_train.csv')
        x_train.columns = ['X','machineID','volt','rotate','pressure','vibration']
        y_train.columns = ['X','failure']
        x_train = x_train.drop('X', axis=1)
        y_train = y_train.drop('X', axis=1)
        y_train = y_train['failure']
        rdmf.fit(x_train, y_train)
        
        self.model = rdmf
        self._init_metrics()

    def _init_metrics(self):
        from prometheus_client import Counter, Histogram, Gauge
        from prometheus_client import REGISTRY
        for metric in list(REGISTRY._collector_to_names):
            REGISTRY.unregister(metric)
        self.PREDICTION_COUNT = Counter('model_predictions_total', 'Total predictions served')
    
    def predict(self, model_input:pd.DataFrame, params = None)->np.array:
        self.PREDICTION_COUNT.inc()
        return self.model.predict(model_input)
    
set_model(SklearnModel())
    