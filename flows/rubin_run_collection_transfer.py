import os
from desc_globus_flow import read_config, collection_id, endpoint_id, \
    function_id, flow_id


__all__ = ["flow_definition", "flow_function", "get_flow_input"]


flow_definition = {
    "Comment": "Rubin RUN collection transfer and ingest",
    "StartAt": "MakeExportYaml",
    "States": {
        "MakeExportYaml": {
            "Comment": "Create the export yaml file for the RUN collection.",
            "Type": "Action",
            "ActionUrl": "https://compute.actions.globus.org",
            "Parameters": {
                "endpoint.$": "$.input.source_compute.endpoint_id",
                "function.$": "$.input.source_compute.function_id",
                "kwargs.$": "$.input.source_compute.arguments"
            },
            "ResultPath": "$.MakeExportYaml_output",
            "WaitTime": 172800,
            "Next": "TransferCollection"
        },
        "TransferCollection": {
            "Comment": "Transfer the RUN collection folder.",
            "Type": "Action",
            "ActionUrl": "https://transfer.actions.globus.org/transfer",
            "Parameters": {
                "source_endpoint.$": "$.input.source_collection.id",
                "destination_endpoint.$": "$.input.destination_collection.id",
                "DATA": [
                    {
                        "source_path.$": "$.input.source_collection.path",
                        "destination_path.$": "$.input.destination_collection.path"
                    }
                ]
            },
            "ResultPath": "$.TransferCollection_output",
            "WaitTime": 18000,
            "Next": "TransferExportYaml"
        },
        "TransferExportYaml": {
            "Comment": "Transfer the export yaml file to destination.",
            "Type": "Action",
            "ActionUrl": "https://transfer.actions.globus.org/transfer",
            "Parameters": {
                "source_endpoint.$": "$.input.source_collection.id",
                "destination_endpoint.$": "$.input.destination_collection.id",
                "DATA": [
                    {
                        "source_path.$": "$.input.source_compute.export_yaml",
                        "destination_path.$": "$.input.destination_compute.export_yaml"
                    }
                ]
            },
            "ResultPath": "$.TransferExportYaml_output",
            "WaitTime": 18000,
            "Next": "RepositoryImport"
        },
        "RepositoryImport": {
            "Comment": "Ingest transferred collection into destination repo.",
            "Type": "Action",
            "ActionUrl": "https://compute.actions.globus.org",
            "Parameters": {
                "endpoint.$": "$.input.destination_compute.endpoint_id",
                "function.$": "$.input.destination_compute.function_id",
                "kwargs.$": "$.input.destination_compute.arguments"
            },
            "ResultPath": "$.RepositoryImport_output",
            "WaitTime": 172800,
            "End": True
        }
    }
}


def make_export_yaml(compute_path=None, repo=None, run_collection=None,
                     weekly=None):
    import subprocess

    export_yaml = f"export_{run_collection.replace('/', '_')}.yaml"

    commands = f"""
    source /cvmfs/sw.lsst.eu/almalinux-x86_64/lsst_distrib/{weekly}/loadLSST.bash
    setup lsst_distrib
    cd {compute_path}
    python create_export_yaml.py {repo} {run_collection} {export_yaml}
    """
    one_line_command = " && ".join(commands.strip().split("\n"))

    subprocess.check_call(one_line_command, shell=True)

    return export_yaml


def repository_import(compute_path=None, repo=None, data_path=None,
                      export_yaml=None):
    import subprocess

    commands = f"""
    source /opt/lsst/software/stack/loadLSST.bash
    setup lsst_distrib
    cd {compute_path}
    butler import --export-file {export_yaml} {repo} {data_path}
    """
    shifter_image = "ghcr.io/lsst/scipipe:al9-w_2026_05"
    one_line_command = " && ".join(commands.strip().split("\n"))
    shifter_command = (f"shifter --image={shifter_image} "
                       f" -- /bin/bash -c '{one_line_command}'")

    subprocess.check_call(shifter_command, shell=True)


flow_function = {
    "make_export_yaml": make_export_yaml,
    "repository_import": repository_import
}


def get_flow_input(config_file):
    config = read_config(config_file)
    flow = config["flow"]

    run_collection = config["run_collection"]
    export_yaml = f"export_{run_collection.replace('/', '_')}.yaml"

    source_collection_path = os.path.join(config["source_data_path"],
                                          config["run_collection"])
    destination_collection_path = os.path.join(config["destination_repo"],
                                               config["run_collection"])

    flow_input = {
        "input": {
            "source_compute": {
                "endpoint_id": endpoint_id(config["source_compute_endpoint_id"]),
                "function_id": function_id(flow, "make_export_yaml"),
                "arguments": {
                    "compute_path": config["source_compute_path"],
                    "repo": config["source_repo"],
                    "run_collection": run_collection,
                    "weekly": config["weekly"]
                },
                "export_yaml": os.path.join(config["source_compute_path"],
                                            export_yaml)
            },
            "source_collection": {
                "id": collection_id(config["source_collection_id"]),
                "path": source_collection_path
            },
            "destination_compute": {
                "endpoint_id": endpoint_id(config["destination_compute_endpoint_id"]),
                "function_id": function_id(flow, "repository_import"),
                "arguments": {
                    "compute_path": config["destination_compute_path"],
                    "repo": config["destination_repo"],
                    "data_path": config["destination_repo"],
                    "export_yaml": export_yaml
                },
                "export_yaml": os.path.join(config["destination_compute_path"],
                                            export_yaml)
            },
            "destination_collection": {
                "id": collection_id(config["destination_collection_id"]),
                "path": destination_collection_path
            }
        }
    }

    return flow_input, flow_id(flow)
