#!/usr/bin/env python
import argparse
from desc_globus_flow import get_flow_module, register_flow_function


parser = argparse.ArgumentParser()
parser.add_argument("flow_def_file", type=str, help="flow definition file")
args = parser.parse_args()

flow_function = get_flow_module(args.flow_def_file).flow_function
register_flow_function(flow_function)
