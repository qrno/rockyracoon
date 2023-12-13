__version__ = "1.0.0"

import json
from pathlib import Path
import logging
import argparse
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from jinja2 import Environment, FileSystemLoader

def render_page(text):
    md = MarkdownIt("commonmark").use(front_matter_plugin)

    context = {"template": "default.html"}
    tokens = md.parse(text)
    if tokens and tokens[0].type == "front_matter":
        front_matter = json.loads(tokens[0].content)
        context.update(front_matter)
    context["body"] = md.render(text)

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(context["template"])
    rendered = template.render(context)

    return rendered

def generate_site(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    for md_file in input_path.rglob("*md"):
        relative = md_file.relative_to(input_path)
        html_path = output_path / relative.with_suffix(".html")
        html_path.parent.mkdir(parents=True, exist_ok=True)

        with md_file.open() as f:
            md_content = f.read()

        html_content = render_page(md_content)
        with html_path.open("w") as f:
            f.write(html_content)

        logging.info(f"Processed: {md_file} -> {html_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a website from markdown files.")
    parser.add_argument("--input", "-i", default="content", help="Input directory with the markdown files.")
    parser.add_argument("--output", "-o", default="output", help="Output directory to store generated HTML files.",)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    input_dir = args.input
    output_dir = args.output

    logging.info(f"Starting build. Input directory: {input_dir}, Output directory {output_dir}")
    generate_site(input_dir, output_dir)
    logging.info("Build complete")
