__version__ = "1.1.1"

import sys
import json
from pathlib import Path
import shutil
import logging
import argparse
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from jinja2 import Environment, FileSystemLoader

def render_page(text):
    md = MarkdownIt("commonmark").use(front_matter_plugin)

    context = {"template": "default.html"}
    tokens = md.parse(text)
    for token in tokens:
        if token.type == "front_matter":
            try:
                front_matter = json.loads(token.content)
                context.update(front_matter)
            except json.decoder.JSONDecodeError as e:
                logging.error(f"Error decoding front matter:\n{token.content}\nError details: {e}")
                sys.exit("Exiting due to error")

    context["body"] = md.render(text)

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(context["template"])
    rendered = template.render(context)

    return rendered

def copy_static_files(input_path, output_path):
    static_path = input_path / "static"
    if static_path.exists():
        shutil.copytree(static_path, output_path / "static", dirs_exist_ok=True)

def generate_site(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    copy_static_files(input_path, output_path)

    for md_file in input_path.rglob("*md"):
        relative = md_file.relative_to(input_path)
        html_path = output_path / relative.with_suffix(".html")
        html_path.parent.mkdir(parents=True, exist_ok=True)

        logging.info(f"Processing: {md_file} -> {html_path}")

        with md_file.open() as f:
            md_content = f.read()

        html_content = render_page(md_content)
        with html_path.open("w") as f:
            f.write(html_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a website from markdown files.")
    parser.add_argument("--input", "-i", default="content", help="Input directory with the markdown files.")
    parser.add_argument("--output", "-o", default="output", help="Output directory to store generated HTML files.",)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    input_dir = args.input
    output_dir = args.output

    logging.info(f"Starting build. Input directory: {input_dir}, Output directory: {output_dir}")
    generate_site(input_dir, output_dir)
    logging.info("Build complete")
