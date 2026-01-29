#!/usr/bin/env python
import argparse
from desc_globus_flow import get_flow_module, register_flow


parser = argparse.ArgumentParser()
parser.add_argument("flow_def_file", type=str, help="flow definition file")
args = parser.parse_args()

flow_definition = get_flow_module(args.flow_def_file).flow_definition
register_flow(flow_definition)
