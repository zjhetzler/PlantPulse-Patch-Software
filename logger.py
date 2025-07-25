import csv
import os
from datetime import datetime
from zoneinfo import ZoneInfo

class BufferedLogger:
    def __init__(self, log_dir="logs", buffer_size=10):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        self.buffer_size = buffer_size
        self.buffer = []

        self._start_new_log_file()

    def _start_new_log_file(self):
        now = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
        self.filename = os.path.join(self.log_dir, f"sensor_log_{now}.csv")
        print("Logging to:", self.filename)

        file_exists = os.path.isfile(self.filename)
        self.file = open(self.filename, mode="a", newline='')
        self.writer = csv.DictWriter(self.file, fieldnames=[
            "timestamp", "unix_timestamp", "patch_id",
            "temperature_ohms", "voc_1_ohms", "voc_2_ohms", "voc_3_ohms",
            "co2_ohms", "optical_ohms", "capacitance_raw"
        ])
        if not file_exists:
            self.writer.writeheader()

    def log(self, record: dict):
        record["timestamp"] = datetime.now(ZoneInfo("America/New_York")).strftime("%d/%m/%Y, %H:%M:%S")
        self.buffer.append(record)
        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def flush(self):
        if self.buffer:
            self.writer.writerows(self.buffer)
            self.buffer.clear()
            self.file.flush()

    def close(self):
        self.flush()
        self.file.close()