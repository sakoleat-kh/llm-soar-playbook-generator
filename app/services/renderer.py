from jinja2 import Environment, FileSystemLoader
from pathlib import Path

env = Environment(
    loader=FileSystemLoader("app/templates")
)

temple = env.get_template("shuffle_workflow.json.j2")

def render_shuffle_workflow(draft, alert_id):

    """
    Render a Shuffle workflow JSON document from a playbook draft
    and alert identifier.
    """

    return temple.render(
        draft=draft,
        alert_id=alert_id,
    )