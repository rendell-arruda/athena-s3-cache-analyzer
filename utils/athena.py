import logging
from botocore.exceptions import ClientError


def list_workgroups(athena_client):
    response = athena_client.list_work_groups()
    workgroups = []
    for workgroup in response.get("WorkGroups", []):
        name = workgroup["Name"]
        state = workgroup["State"]

        try:
            detail = athena_client.get_work_group(WorkGroup=name)
            output_location = detail["WorkGroup"]["Configuration"][
                "ResultConfiguration"
            ]["OutputLocation"]
        except ClientError as e:
            logging.warning(
                f"Could not get details for workgroup '{name}': {e.response['Error']['Code']}"
            )
            output_location = "N/A"
        except KeyError:
            logging.warning(f"Workgroup '{name}' has no output location configured.")
            output_location = "N/A"

        workgroups.append(
            {"workgroup": name, "state": state, "output_location": output_location}
        )

    return workgroups


def list_execution_buckets(athena_client, max_executions):
    response = athena_client.list_query_executions(MaxResults=max_executions)
    executions_ids = response.get("QueryExecutionIds", [])
    print(f"Found {len(executions_ids)} query executions.")
