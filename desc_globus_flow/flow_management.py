import os
import sys
import importlib
import globus_compute_sdk
from globus_sdk import FlowsClient, UserApp
from .uuid_database import UuidDatabase


__all__ = ["get_flow_module", "register_flow", "update_flow",
           "register_flow_functions", "collection_id", "endpoint_id",
           "function_id", "flow_id"]


UUID_DB = UuidDatabase(os.environ["GLOBUS_UUID_DB_FILE"])


def collection_id(config):
    row = {k: v for k, v in zip(("site", "collection"), config.split(":"))}
    return UUID_DB.get("collections", row)


def endpoint_id(config):
    row = {k: v for k, v in zip(("site", "endpoint"), config.split(":"))}
    return UUID_DB.get("endpoints", row)


def function_id(flow, function):
    row = {"flow": flow, "function": function}
    return UUID_DB.get("functions", row)


def flow_id(flow):
    row = {"flow": flow}
    return os.environ.get("GLOBUS_FLOW_ID",
                          UUID_DB.get("flows", row))


def get_flow_module(definition_file):
    file_path, module_name = os.path.split(os.path.abspath(definition_file))
    module_name = module_name.strip(".py")
    sys.path.insert(0, file_path)
    module = importlib.import_module(module_name)
    sys.path.pop(0)
    return module


# Public Globus thick client for authentication
AUTH_CLIENT_ID = "f818e8c5-61ba-4f70-8237-a8e69f266ae7"


def update_flow(module, title=None, app_name="lsst-desc-flow-app"):
    flow = module.__name__
    flow_definition = module.flow_definition

    flows_client = FlowsClient(
        app=UserApp(
            client_id=AUTH_CLIENT_ID,
            app_name=app_name
        )
    )

    if title is None:
        title = flow_definition["Comment"]
    flows_client.update_flow(
        flow_id(flow),
        definition=flow_definition,
        title=title
    )


def register_flow(module, title=None, app_name="lsst-desc-flow-app"):
    flow_name = module.__name__
    flow_definition = module.flow_definition

    flows_client = FlowsClient(
        app=UserApp(
            client_id=AUTH_CLIENT_ID,
            app_name=app_name
        )
    )

    if title is None:
        title = flow_definition["Comment"]
    flow = flows_client.create_flow(
        title=title,
        definition=flow_definition,
        input_schema={}  # This can be set to restrict the flow input format
    )

    # Save the flow UUID
    flow_id = flow["id"]
    UUID_DB.set(flow_id, "flows", {"flow": flow_name})
    print(f"\nFlow registered with UUID - {flow_id}")
    print(f"https://app.globus.org/flows/{flow_id}")


def register_flow_functions(module):
    import types
    import __main__

    flow = module.__name__
    flow_functions = module.flow_functions

    gcc = globus_compute_sdk.Client()

    for label, func in flow_functions.items():
        # Re-bind each function to the __main__ namespace so that they
        # can be serialized without requiring the flow module to be
        # accessible at the compute site.
        my_func = types.FunctionType(
            func.__code__,
            __main__.__dict__,
            name=func.__name__,
            argdefs=func.__defaults__,
            closure=func.__closure__
        )
        func_id = gcc.register_function(my_func)
        UUID_DB.set(func_id, "functions", {"flow": flow, "function": label})
        print(f"{label} registered with UUID {func_id}")
