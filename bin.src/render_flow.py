#!/usr/bin/env python
import os
import argparse
from pprint import pprint
from desc_globus_flow import render_flow


parser = argparse.ArgumentParser()
parser.add_argument("flow_def_file", type=str, help="flow definition file")
parser.add_argument("--outfile", type=str, default=None,
                    help="Name of pdf output file.  Default: <flow_name>.pdf")
parser.add_argument("--save_dot", action="store_true",
                    help="Retain the dot file.")
args = parser.parse_args()

if args.outfile is None:
    flow_name = os.path.split(os.path.abspath(args.flow_def_file))[-1]\
                       .split(".")[0]
    outfile = f"{flow_name}.pdf"
else:
    outfile = args.outfile

render_flow(args.flow_def_file, outfile=outfile)

if not args.save_dot:
    os.remove(outfile.strip(".pdf"))
