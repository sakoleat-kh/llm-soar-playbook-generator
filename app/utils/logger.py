import logging
import os

os.makedirs("data", exist_ok=True)

logger = logging.getLogger("soar")
logger.setLevel(logging.INFO)

class DefaultExtrasFilter(logging.Filter):
    def filter(self, record):

        record.alert_id = getattr(record, "alert_id", "-")
        record.technique_id = getattr(record, "technique_id", "-")
        record.confidence = getattr(record, "confidence", "-")
        record.path = getattr(record, "path", "-")

        return True

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(message)s | "
    "alert_id=%(alert_id)s | "
    "technique=%(technique_id)s | "
    "confidence=%(confidence)s | "
    "path=%(path)s"
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.addFilter(DefaultExtrasFilter())

file_handler = logging.FileHandler(
    "data/system.log",
    encoding="utf-8"
)

file_handler.setFormatter(formatter)
file_handler.addFilter(DefaultExtrasFilter())

if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)