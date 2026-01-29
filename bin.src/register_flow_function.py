#!/usr/bin/env python
import argparse
import types
import __main__
from desc_globus_flow import get_flow_module, register_flow_function


parser = argparse.ArgumentParser()
parser.add_argument("flow_def_file", type=str, help="flow definition file")
args = parser.parse_args()

func = get_flow_module(args.flow_def_file).flow_function

# Re-bind the function to the __main__ namespace so that it can be
# serialized without requiring the flow module to be accessible at the
# compute site.
flow_function = types.FunctionType(
    func.__code__,
    __main__.__dict__,
    name=func.__name__,
    argdefs=func.__defaults__,
    closure=func.__closure__
)

register_flow_function(flow_function)
