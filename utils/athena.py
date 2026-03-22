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
    logging.info(f"Found {len(executions_ids)} query executions in region.")

    bucket_name_list = {}
    for execution_id in executions_ids:
        try:
            detail = athena_client.get_query_execution(QueryExecutionId=execution_id)
            output_location = detail["QueryExecution"]["ResultConfiguration"][
                "OutputLocation"
            ]
            bucket_name = output_location.rsplit("/", 1)[0]
            last_seen = detail["QueryExecution"]["Status"].get(
                "CompletionDateTime", "N/A"
            )

            if bucket_name in bucket_name_list:
                bucket_name_list[bucket_name]["total_executions"] += 1
                if last_seen and last_seen > bucket_name_list[bucket_name]["last_seen"]:
                    bucket_name_list[bucket_name]["last_seen"] = last_seen
            else:
                bucket_name_list[bucket_name] = {
                    "total_executions": 1,
                    "last_seen": last_seen,
                }

        except ClientError as e:
            logging.error(
                f"Error getting execution '{execution_id}': {e.response['Error']['Code']}"
            )
        except KeyError:
            logging.warning(f"Execution '{execution_id}' has no output location.")

    return bucket_name_list
