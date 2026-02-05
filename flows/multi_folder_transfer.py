from desc_globus_flow import read_config, collection_id, flow_id


__all__ = ["flow_definition", "flow_functions", "get_flow_input"]


flow_definition = {
    "Comment": "Multi-item transfers",
    "StartAt": "CheckIfListEmpty",
    "States": {
        "CheckIfListEmpty": {
            "Type": "Choice",
            "Choices": [
                {
                    "Variable": "$.input.folder_list[0]",
                    "IsPresent": True,
                    "Next": "TransferSingleItem"
                }
            ],
            "Default": "AllDone"
        },
        "TransferSingleItem": {
            "Type": "Action",
            "ActionUrl": "https://transfer.actions.globus.org/transfer",
            "Parameters": {
                "source_endpoint.$": "$.input.source_collection.id",
                "destination_endpoint.$": "$.input.destination_collection.id",
                "DATA": [
                    {
                        "DATA_TYPE": "transfer_item",
                        "source_path.=": "input.source_collection.path + input.folder_list[0]",
                        "destination_path.=": "input.destination_collection.path + input.folder_list[0]"
                    }
                ]
            },
            "ResultPath": "$.last_transfer",
            "Next": "RemoveProcessedItem"
        },
        "RemoveProcessedItem": {
            "Type": "ExpressionEval",
            "Parameters": {
                "folder_list.=": "input.folder_list[1:]",
                "source_collection.=": "{'id': input.source_collection.id, 'path': input.source_collection.path}",
                "destination_collection.=": "{'id': input.destination_collection.id, 'path': input.destination_collection.path}"
            },
            "ResultPath": "$.input",
            "Next": "CheckIfListEmpty"
        },
        "AllDone": {
            "Type": "Pass",
            "End": True
        }
    }
}


flow_functions = {}


def get_flow_input(config_file):
    config = read_config(config_file)

    if "folder_list" in config:
        folder_list = config["folder_list"]
    elif "folder_list_file" in config:
        with open(config["folder_list_file"]) as fobj:
            folder_list = [_.strip() for _ in fobj.readlines()]
    else:
        raise RuntimeError(f"No folder_list[_file] in {config_file}")

    flow_input = {
        "input": {
            "folder_list": folder_list,
            "source_collection": {
                "id": collection_id(config["source_collection"]),
                "path": config["source_base_path"],
            },
            "destination_collection": {
                "id": collection_id(config["destination_collection"]),
                "path": config["destination_base_path"],
            },
        }
    }

    return flow_input, flow_id(config["flow"])
