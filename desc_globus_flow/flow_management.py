import os
import sys
import importlib
import globus_compute_sdk
from globus_sdk import FlowsClient, UserApp


__all__ = ["get_flow_module", "register_flow", "update_flow",
           "register_flow_function"]


def get_flow_module(definition_file):
    file_path, module_name = os.path.split(os.path.abspath(definition_file))
    module_name = module_name.strip(".py")
    sys.path.insert(0, file_path)
    module = importlib.import_module(module_name)
    sys.path.pop(0)
    return module


# Public Globus thick client for authentication
AUTH_CLIENT_ID = "f818e8c5-61ba-4f70-8237-a8e69f266ae7"


def update_flow(flow_definition, flow_id, title=None, app_name="lsst-desc-flow-app"):
    flows_client = FlowsClient(
        app=UserApp(
            client_id=AUTH_CLIENT_ID,
            app_name=app_name
        )
    )

    if title is None:
        title = flow_definition["Comment"]
    flow = flows_client.update_flow(
        flow_id,
        definition=flow_definition,
        title=title
    )


def register_flow(flow_definition, title=None, app_name="lsst-desc-flow-app"):
    # Create authenticated Flows client. NOTE: This can be changed to
    # use client's secrets to avoid having to authenticate.
    flows_client = FlowsClient(
        app=UserApp(
            client_id=AUTH_CLIENT_ID,
            app_name=app_name
        )
    )

    # Register flow
    if title is None:
        title = flow_definition["Comment"]
    flow = flows_client.create_flow(
        title=title,
        definition=flow_definition,
        input_schema={}  # This can be set to restrict the flow input format
    )

    # Collect the flow UUID
    flow_id = flow["id"]
    print(f"\nFlow registered with UUID - {flow_id}")
    print(f"https://app.globus.org/flows/{flow_id}")

    # Write flow UUID in a file
    uuid_file_name = "uuid_flow.txt"
    with open(uuid_file_name, "w") as file:
        file.write(flow_id)
        file.write("\n")
    print(f"The UUID is stored in {uuid_file_name}.\n")


def register_flow_function(flow_function):
    gcc = globus_compute_sdk.Client()

    # Register the function
    compute_function_id = gcc.register_function(flow_function)

    # Write function UUID in a file
    uuid_file_name = "uuid_flow_function.txt"
    with open(uuid_file_name, "w") as file:
        file.write(compute_function_id)
        file.write("\n")
    print(f"Function registered with UUID - {compute_function_id}")
    print(f"The UUID is stored in {uuid_file_name}.\n")
