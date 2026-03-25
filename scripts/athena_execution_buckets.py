import csv
import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError
from utils.athena import list_execution_buckets
from utils.s3 import get_bucket_size
from utils.s3 import bytes_to_gb_and_cost

AWS_PROFILE = "default"
REGIONS = ["us-east-1", "sa-east-1"]
MAX_EXECUTIONS = 50
S3_PRICE_PER_GB = {
    "us-east-1": 0.023,
    "sa-east-1": 0.0245,
}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger("botocore").setLevel(logging.WARNING)


def main():
    rows = []
    for region in REGIONS:
        logging.info(f"Collecting Athena workgroups in region: {region}")
        try:
            session = boto3.Session(profile_name=AWS_PROFILE, region_name=region)
            athena_client = session.client("athena")
            executions = list_execution_buckets(
                athena_client=athena_client, max_executions=MAX_EXECUTIONS
            )

            for bucket, info in executions.items():
                bucket_name = bucket.replace("s3://", "")
                cloudwatch_client = session.client("cloudwatch")
                size_bytes = get_bucket_size(cloudwatch_client, bucket_name)
                price_per_gb = S3_PRICE_PER_GB.get(region, 0.023)
                size_gb, estimated_cost = bytes_to_gb_and_cost(size_bytes, price_per_gb)

                rows.append(
                    {
                        "region": region,
                        "bucket": bucket,
                        "executions": info["total_executions"],
                        "last_seen": info["last_seen"],
                        "size_bytes": size_bytes,
                        "size_gb": size_gb,
                        "estimated_cost": estimated_cost,
                    }
                )
                logging.info(
                    f"  Bucket: {bucket} | Executions: {info['total_executions']} | Last seen: {info['last_seen']} | Size (bytes): {size_bytes}"
                )
        except ClientError as e:
            logging.error(
                f"Error connecting to Athena in region '{region}': {e.response['Error']['Code']}"
            )
            continue

    # gerar CSV aqui
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"output/athena_execution_buckets_{timestamp}.csv"

    with open(filename, "w", newline="") as csvfile:
        fieldnames = [
            "region",
            "bucket",
            "executions",
            "last_seen",
            "size_bytes",
            "size_gb",
            "estimated_cost",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    logging.info(f"CSV file '{filename}' generated successfully.")


if __name__ == "__main__":
    main()
