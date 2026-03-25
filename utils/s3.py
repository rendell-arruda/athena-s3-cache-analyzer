import boto3
import logging
from botocore.exceptions import ClientError
from datetime import datetime, timedelta, timezone


def get_bucket_size(cloudwatch_client, bucket_name):
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=2)
    try:
        response = cloudwatch_client.get_metric_statistics(
            Namespace="AWS/S3",
            MetricName="BucketSizeBytes",
            Dimensions=[
                {"Name": "BucketName", "Value": bucket_name},
                {"Name": "StorageType", "Value": "StandardStorage"},
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,
            Statistics=["Average"],
        )
        datapoints = response.get("Datapoints", [])
        if not datapoints:
            return 0
        latest = sorted(datapoints, key=lambda x: x["Timestamp"])[-1]
        size_bytes = latest["Average"]
        return size_bytes

    except ClientError as e:
        logging.error(
            f"Error occurred while fetching bucket size for {bucket_name}: {e}"
        )
        return 0


def bytes_to_gb_and_cost(size_bytes, price_per_gb=0.0245):
    size_gb = size_bytes / (1024**3)
    # Custo estimado com base na taxa de $0.0245 por GB-mês para armazenamento S3 Standard em sa-east-1 (verifique a taxa atual para sua região)
    estimated_cost = size_gb * price_per_gb
    return round(size_gb, 10), round(estimated_cost, 10)
