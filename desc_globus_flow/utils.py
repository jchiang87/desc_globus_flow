import yaml


__all__ = ["read_config"]


def read_config(yaml_file):
    with open(yaml_file) as fobj:
        config = yaml.safe_load(fobj)
    config["flow"] = config["flow_definition_file"].split("/")[-1][:-len(".py")]
    return config
