#!/usr/bin/env python
import argparse
from desc_globus_flow import get_flow_module, run_flow


parser = argparse.ArgumentParser()
parser.add_argument("flow_def_file", type=str, help="flow definition file")
parser.add_argument("flow_config", type=str, help="flow configuration file")
args = parser.parse_args()

get_flow_input = get_flow_module(args.flow_def_file).get_flow_input
flow_input, flow_id = get_flow_input(args.flow_config)

run_flow(flow_input, flow_id)
