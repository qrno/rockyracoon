from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from jinja2 import Environment, FileSystemLoader
import json
from pathlib import Path

def render_page(text):
    md = MarkdownIt('commonmark').use(front_matter_plugin)

    context = {}
    tokens = md.parse(text)
    if len(tokens) >= 1 and tokens[0].type == 'front_matter':
        context = json.loads(tokens[0].content)

    if 'template' not in context:
        context['template'] = 'default.html'
    context['body'] = md.render(text)

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(context['template'])
    rendered = template.render(context)

    return rendered

def mirror_build(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    for file in input_path.rglob('*md'):
        relative = file.relative_to(input_path)
        html_path = output_path / relative.with_suffix('.html')
        html_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file) as md_file:
            md_content = md_file.read()

        html_content = render_page(md_content)

        with open(html_path, 'w') as html_file:
            html_file.write(html_content)

input_dir = 'content'
output_dir = 'output'

mirror_build(input_dir, output_dir)
