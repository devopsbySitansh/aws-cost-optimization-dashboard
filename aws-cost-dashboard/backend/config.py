"""Application Configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AWS_REGION              = os.getenv("AWS_REGION", "ap-south-1")
    DEBUG                   = os.getenv("FLASK_ENV", "production") == "development"
    ALERT_THRESHOLD_CPU     = float(os.getenv("ALERT_THRESHOLD_CPU", 20))
    CLOUDWATCH_PERIOD       = int(os.getenv("CLOUDWATCH_PERIOD", 3600))
