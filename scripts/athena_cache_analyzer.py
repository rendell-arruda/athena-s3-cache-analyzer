import boto3
import logging
from botocore.exceptions import ClientError
from utils.athena import list_workgroups

AWS_PROFILE = "default"

REGIONS = ["us-east-1", "sa-east-1"]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    for region in REGIONS:
        logging.info(f"Collecting Athena workgroups in region: {region}")
        try:
            session = boto3.Session(profile_name=AWS_PROFILE, region_name=region)
            athena_client = session.client("athena")
            workgroups = list_workgroups(athena_client)
        except ClientError as e:
            logging.error(
                f"Error connecting to Athena in region '{region}': {e.response['Error']['Code']}"
            )
            continue

        for wg in workgroups:
            logging.info(
                f"  Workgroup: {wg['workgroup']} | State: {wg['state']} | Output: {wg['output_location']}"
            )


if __name__ == "__main__":
    main()
