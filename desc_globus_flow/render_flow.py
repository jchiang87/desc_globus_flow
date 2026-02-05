import json
from graphviz import Digraph
from desc_globus_flow import get_flow_module

__all__ = ["render_flow"]


def render_flow(flow_def_file, outfile="rendered_flow.pdf", view=True):
    if flow_def_file.endswith('.py'):
        flow = get_flow_module(flow_def_file).flow_definition
    elif flow_def_file.endswith('.json'):
        with open(flow_def_file) as fobj:
            flow = json.load(fobj)

    dot = Digraph(flow["Comment"])
    for name, state in flow['States'].items():
        dot.node(name)
        if "Next" in state:
            dot.edge(name, state["Next"])
        elif "Default" in state:
            dot.edge(name, state["Default"])
        if "Choices" in state:
            for item in state["Choices"]:
                dot.edge(name, item["Next"])
        if "Catch" in state:
            for item in state["Catch"]:
                dot.edge(name, item["Next"], style="dotted")

    dot.render(outfile.strip(".pdf"), view=view)
