import os
from desc_globus_flow import read_config


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
                        "source_path.$": "$.input.source_compute.path",
                        "destination_path.$": "$.input.destination_compute.path"
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
    import textwrap

    script_text = textwrap.dedent(
        """
        import lsst.daf.butler as daf_butler
        from lsst.daf.butler.script import queryDatasetTypes


        def create_export_yaml(repo, run_collection, export_file, dest_dir='.'):
            butler = daf_butler.Butler(repo, collections=[run_collection])
            dstypes = queryDatasetTypes(repo, False, ..., [run_collection])
            refs = set()
            with butler.export(directory=dest_dir, filename=export_file,
                               transfer=None) as exporter:
            for dstype in dstypes["name"]:
                my_refs = set(butler.registry.queryDatasets(dstype))
                refs = refs.union(my_refs)
            refs = list(refs)
            exporter.saveCollection(run_collection)
            exporter.saveDatasets(refs)


        if __name__ == '__main__':
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("repo", type=str, help="Data repository")
            parser.add_argument("run_collection", type=str, help="RUN collection")
            parser.add_argument("export_file", type=str, help="Export file name")

            args = parser.parse_args()
            create_export_yaml(args.repo, args.run_collection, args.export_file)
        """
    )

    export_yaml = f"export_{run_collection.replace('/', '_')}.yaml"

    commands = f"""
    source /cvmfs/sw.lsst.eu/almalinux-x86_64/lsst_distrib/{weekly}/loadLSST.bash
    setup lsst_distrib
    cd {compute_path}
    echo {script_text} > create_export_yaml.py
    python create_export_yaml.py {repo} {run_collection} {export_yaml}
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

    subprocess.run(one_line_command, **kwargs)

    return export_yaml


def repository_import(compute_path=None, repo=None, data_path=None,
                      export_yaml=None, weekly=None):
    import subprocess

    commands = f"""
    source /cvmfs/sw.lsst.eu/almalinux-x86_64/lsst_distrib/{weekly}/loadLSST.bash
    setup lsst_distrib
    cd {compute_path}
    butler import --export-file {export_yaml} {repo} {data_path}
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

    subprocess.run(one_line_command, **kwargs)


flow_function = {
    "make_export_yaml": make_export_yaml,
    "repository_import": repository_import
}


def get_flow_input(config_file):
    config = read_config(config_file)

    run_collection = config["run_collection"]
    export_yaml = f"export_{run_collection.replace('/', '_')}.yaml"

    flow_input = {
        "input": {
            "source_compute": {
                "endpoint_id": config["source_compute_endpoint_id"],
                "function_id": config["source_function_id"],
                "arguments": {
                    "compute_path": config["source_compute_path"],
                    "repo": config["source_repo"],
                    "run_collection": run_collection,
                    "weekly": config["weekly"]
                }
            },
            "source_collection": {
                "id": config["source_collection_id"],
                "path": config["source_data_path"]
            },
            "destination_compute": {
                "endpoint_id": config["destination_compute_endpoint_id"],
                "function_id": config["destination_function_id"],
                "arguments": {
                    "compute_path": config["destination_compute_path"],
                    "repo": config["destination_repo"],
                    "data_path": config["destination_repo"],
                    "export_yaml": export_yaml,
                    "weekly": config["weekly"]
                }
            },
            "destination_collection": {
                "id": config["destination_collection_id"],
                "path": config["destination_repo"]
            }
        }
    }

    return flow_input, config["flow_id"]
