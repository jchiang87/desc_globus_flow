#!/usr/bin/env python
import os
import argparse
from desc_globus_flow import get_flow_module, register_flow, update_flow


parser = argparse.ArgumentParser()
parser.add_argument("operation", choices=["register", "update"],
                    help="Flow operation to perform")
parser.add_argument("flow_def_file", type=str, help="flow definition file")
parser.add_argument("--flow_id", type=str, default=None,
                    help="Flow id as UUID string")
args = parser.parse_args()

flow_definition = get_flow_module(args.flow_def_file).flow_definition

if args.operation == "register":
    register_flow(flow_definition)
elif args.operation == "update":
    if args.flow_id is None:
        # Read the flow_id from the enviroment variable.
        try:
            flow_id = os.environ["GLOBUS_FLOW_ID"]
        except KeyError:
            raise ArgumentError("flow_id not found")
    update_flow(flow_definition, flow_id)
