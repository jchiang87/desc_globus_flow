#!/usr/bin/env python
import argparse
import yaml
from desc_globus_flow import read_config, get_flow_module, run_flow


parser = argparse.ArgumentParser()
parser.add_argument("flow_config", type=str, help="flow configuration file")
parser.add_argument("--flow_def_file", type=str, default=None, help="flow definition file")
args = parser.parse_args()

config = read_config(args.flow_config)

flow_def_file = (args.flow_def_file if args.flow_def_file is not None
                 else config['flow_definition_file'])

get_flow_input = get_flow_module(flow_def_file).get_flow_input
flow_input, flow_id = get_flow_input(args.flow_config)

run_flow(flow_input, flow_id)
