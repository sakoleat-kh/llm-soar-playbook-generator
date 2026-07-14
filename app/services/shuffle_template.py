from pathlib import Path
from jinja2 import Environment, FileSystemLoader

template_dir = Path(__file__).parent.parent / "templates"

env = Environment(
    loader=FileSystemLoader(template_dir)
)

template = env.get_template("shuffle_workflow.json.j2")

def render_shuffle_workflow(data: dict) -> str:
    return template.render(**data)