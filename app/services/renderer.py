from jinja2 import Environment, FileSystemLoader
from pathlib import Path

env = Environment(
    loader=FileSystemLoader("app/templates")
)

temple = env.get_template("shuffle_workflow.json.j2")

def render_shuffle_workflow(draft, alert_id):
    return temple.render(
        draft=draft,
        alert_id=alert_id,
    )