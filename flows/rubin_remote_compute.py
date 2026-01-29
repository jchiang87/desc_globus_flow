import os
from desc_globus_flow import read_config


__all__ = ["flow_definition", "flow_function", "get_flow_input"]


flow_definition = {
    "Comment": "Remote compute for Rubin pipelines",
    "StartAt": "TransferInputs",
    "States": {
        "TransferInputs": {
            "Comment": "Transfer folder from repository to compute site.",
            "Type": "Action",
            "ActionUrl": "https://transfer.actions.globus.org/transfer",
            "Parameters": {
                "source_endpoint.$": "$.input.repository_collection.id",
                "destination_endpoint.$": "$.input.compute_collection.id",
                "DATA": [
                    {
                        "source_path.$": "$.input.repository_collection.path",
                        "destination_path.$": "$.input.compute_collection.path",
                        "recursive": True,
                    }
                ]
            },
            "ResultPath": "$.TransferInputs_output",
            "WaitTime": 18000,
            "Next": "Compute"
        },
        "Compute": {
            "Comment": "Run analysis at the HPC facility.",
            "Type": "Action",
            "ActionUrl": "https://compute.actions.globus.org/",
            "Parameters": {
                "endpoint.$": "$.input.compute.endpoint_id",
                "function.$": "$.input.compute.function_id",
                "kwargs.$": "$.input.compute.arguments"
            },
            "ResultPath": "$.Compute_output",
            "WaitTime": 172800,
            "Next": "TransferResults"
        },
        "TransferResults": {
            "Comment": "Transfer results folder back to the repository.",
            "Type": "Action",
            "ActionUrl": "https://transfer.actions.globus.org/transfer",
            "Parameters": {
                "source_endpoint.$": "$.input.compute_collection.id",
                "destination_endpoint.$": "$.input.repository_collection.id",
                "DATA": [
                    {
                        "source_path.$": "$.Compute_output.details.result[0][0]",
                        "destination_path.$": "$.Compute_output.details.result[0][1]",
                        "recursive": True,
                    }
                ]
            },
            "ResultPath": "$.TransferResults_output",
            "WaitTime": 18000,
            "End": True
        }
    }
}


def flow_function(weekly=None, compute_path=None, repository_path=None):
    import os
    import subprocess

    commands = f"""
    source /cvmfs/sw.lsst.eu/almalinux-x86_64/lsst_distrib/{weekly}/loadLSST.bash
    setup lsst_distrib
    cd {compute_path}
    mkdir -p logs
    (bps submit bps_stage1.yaml) &> logs/bps_stage1.log
    """
    kwargs = {
        "shell": True,
        "check": True,
        "text": True,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "executable": "/bin/bash"
    }

    one_line_command = " && ".join(commands.strip().split("\n"))

    result = subprocess.run(one_line_command, **kwargs)

    return (compute_path, repository_path)


def get_flow_input(config_file):
    config = read_config(config_file)

    compute_path = os.path.join(config["compute_base_path"],
                                config["payload_data"]["inputs_folder"])
    compute_path = compute_path.rstrip("/") + "/"
    repository_path = os.path.join(config["repository_base_path"],
                                   config["payload_data"]["outputs_folder"])
    repository_path = repository_path.rstrip("/") + "/"
    arguments = {
        "weekly": config["payload_data"]["weekly"],
        "compute_path": compute_path,
        "repository_path": repository_path
    }

    flow_input = {
        "input": {
            "repository_collection": {
                "id": config["repository_collection_id"],
                "path": config["repository_base_path"],
            },
            "compute_collection": {
                "id": config["compute_collection_id"],
                "path": config["compute_base_path"],
            },
            "compute": {
                "endpoint_id": config["compute_endpoint_id"],
                "function_id": config["flow_function_id"],
                "arguments": arguments,
            }
        }
    }

    return flow_input, config["flow_id"]
