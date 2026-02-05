#!/usr/bin/env python
import argparse
from desc_globus_flow import get_flow_module, register_flow, update_flow


parser = argparse.ArgumentParser()
parser.add_argument("operation", choices=["register", "update"],
                    help="Flow operation to perform")
parser.add_argument("flow_def_file", type=str, help="flow definition file")
args = parser.parse_args()

module = get_flow_module(args.flow_def_file)

if args.operation == "register":
    register_flow(module)
elif args.operation == "update":
    update_flow(module)
