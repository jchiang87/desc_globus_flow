import yaml


__all__ = ["read_config"]


def read_config(yaml_file):
    with open(yaml_file) as fobj:
        config = yaml.safe_load(fobj)
    return config
