#!/usr/bin/env python
import argparse
from desc_globus_flow import get_flow_module, register_flow_functions


parser = argparse.ArgumentParser()
parser.add_argument("flow_def_file", type=str, help="flow definition file")
args = parser.parse_args()

module = get_flow_module(args.flow_def_file)

if not hasattr(module, "flow_function"):
    print(f"No flow function found in {module.__name__}")
else:
    register_flow_functions(module)
