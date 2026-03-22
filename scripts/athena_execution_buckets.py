import csv
import boto3
import logging
from botocore.exceptions import ClientError
from utils.athena import list_execution_buckets
from datetime import datetime


AWS_PROFILE = "default"
REGIONS = ["us-east-1", "sa-east-1"]
MAX_EXECUTIONS = 50

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
                rows.append(
                    {
                        "region": region,
                        "bucket": bucket,
                        "executions": info["total_executions"],
                        "last_seen": info["last_seen"],
                    }
                )
                logging.info(
                    f"  Bucket: {bucket} | Executions: {info['total_executions']} | Last seen: {info['last_seen']}"
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
        fieldnames = ["region", "bucket", "executions", "last_seen"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    logging.info(f"CSV file '{filename}' generated successfully.")


if __name__ == "__main__":
    main()
