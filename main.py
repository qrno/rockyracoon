from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
import json

from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape

md = MarkdownIt('commonmark').use(front_matter_plugin)

text = ("""\
---
{
    "title": "Hello World",
    "subtitle": "It's a beautiful day",
    "date": "2023-12-01",
    "update": "2023-12-01",
    "author": "Eduardo Quirino",
    "template" : "article.jinja"
}
---


# Flamengo

oi

## heheeh

- a
- b
- c

<!-- term being defined when used in a definition -->
<dl>
  <dt>Semantic HTML</dt>
  <dd>
    Use the elements based on their <b>semantic</b> meaning, not their
    appearance.
  </dd>
</dl>


""")

def render_page(text):
    tokens = md.parse(text)
    if len(tokens) == 0 or tokens[0].type != 'front_matter':
        raise ValueError("Page must contain a front matter")

    context = json.loads(tokens[0].content)
    context['body'] = md.render(text)

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(context['template'])
    rendered = template.render(context)

    return rendered


html_text = render_page(text)
from pathlib import Path
Path("output.html").write_text(html_text)
