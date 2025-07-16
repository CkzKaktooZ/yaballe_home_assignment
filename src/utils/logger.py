import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("yaballe_app")
logger.setLevel(logging.INFO)

# --- Console Handler ---
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# --- File Handler (optional) ---
file_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "app.log"),
    maxBytes=1_000_000,  # 1MB per file
    backupCount=3,
)
file_handler.setLevel(logging.INFO)

# --- Formatter ---
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# --- Add Handlers ---
if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
