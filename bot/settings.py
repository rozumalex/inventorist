import pathlib
import yaml
from dotmap import DotMap


BASE_DIR = pathlib.Path(__file__).parent.parent
config_path = BASE_DIR / 'config.yaml'


def get_config(path):
    with open(path) as file:
        return yaml.safe_load(file)


config = DotMap(get_config(config_path))
