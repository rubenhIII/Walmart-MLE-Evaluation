import pandas as pd
import json
import random

import logging

class V2_PROTOCOL_ENCODER:
    def __init__(self):
        self.data_frame = None
        self.logger = logging.getLogger(name=__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def encode(self, data_frame: pd.DataFrame):
        type_mapping = {
        'int64': 'INT64',
        'float64': 'FP64',
        'object': 'BYTES'  # For strings
        }
        # Get inputs
        self.data_frame = data_frame
        inputs = []
        columns = self.data_frame.columns
        for col in columns:
            values = self.data_frame[col].values.tolist()
            col_type = type_mapping[str(self.data_frame[col].dtype)]
            col_shape = self.data_frame[col].shape

            input_by_column = {
                "name": str(col),
                "datatype": str(col_type),
                "shape": list(col_shape),
                "data": list(values)
            }
            inputs.append(input_by_column)

        v2_request = {
            "parameters": {
                "content_type": "pd"
            },
            "inputs": inputs,
        }

        return v2_request

