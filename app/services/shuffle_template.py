from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from app.services.generator import PlaybookDraft

template_dir = Path(__file__).parent.parent / "templates"

env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=False,
)

template = env.get_template("shuffle_workflow.json.j2")

def render_shuffle_workflow(
        draft: PlaybookDraft,
        alert_id: str,
) -> str:
    return template.render(
        draft=draft,
        alert_id=alert_id,
    )