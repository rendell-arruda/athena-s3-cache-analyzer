import boto3
import logging
from botocore.exceptions import ClientError

REGIONS = ["us-east-1", "sa-east-1"]  # Add more regions as needed

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
