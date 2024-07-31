__version__ = "2.0.0b"

import sys
import tomllib
from pathlib import Path
import shutil
import logging
import argparse
import datetime
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter.index import front_matter_plugin
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

md_parser = MarkdownIt("commonmark").use(front_matter_plugin)
jinja_env = Environment()

def render_page(source_md : str) -> str:
    context = {}

    tokens = md_parser.parse(source_md)

    has_front_matter = False
    for token in tokens:
        if token.type == "front_matter":
            has_front_matter = True

            try:
                front_matter = tomllib.loads(token.content)
            except tomllib.TOMLDecodeError:
                error_msg = "Error decoding front matter:\n{token.content}\nError details: {e}"
                logging.error(error_msg)
                raise ValueError(error_msg)

            context.update(front_matter)

    if not has_front_matter:
        error_msg = "Front matter not found"
        logging.error(error_msg)
        raise ValueError(error_msg)

    if 'template' not in context:
        error_msg = "Template not in front matter, using \"default.html\""
        logging.warning(error_msg)

    context["rr_body"] = md_parser.render(source_md)
    context["rr_version"] = __version__
    context["rr_now"] = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        template = jinja_env.get_template(context["template"])
    except TemplateNotFound as e:
        error_msg = f"Error getting template {e}"
        logging.error(error_msg)
        raise ValueError(error_msg)

    rendered = template.render(context)
    return rendered

def copy_static_files(static_path: Path, output_path : Path) -> None:
    try:
        static_dest_path = output_path / static_path.name
        logging.info(f"Copying static directory: {static_path} -> {static_dest_path}")
        shutil.copytree(static_path, static_dest_path, dirs_exist_ok=True)
    except Exception as e:
        logging.critical(f"Error copying static files: {e}")
        raise e

def process_markdown_files(content_path : Path, output_path : Path) -> None:
    for md_file in content_path.rglob("*md"):
        relative = md_file.relative_to(content_path)
        html_path = output_path / relative.with_suffix(".html")
        html_path.parent.mkdir(parents=True, exist_ok=True)

        logging.info(f"Processing: {md_file} -> {html_path}")

        try:
            with md_file.open() as f:
                md_content = f.read()
        except Exception as e:
            logging.error(f"Could not read {md_file}: {e}")
            continue

        try:
            html_content = render_page(md_content)
        except Exception as e:
            logging.error(f"Could not render {md_file}: {e}.")
            continue

        try:
            with html_path.open("w") as f:
                f.write(html_content)
        except Exception as e:
            logging.error(f"Could not write to {html_path}: {e}")
            continue

def generate_site(content_path : Path, templates_path : Path, static_path : Path, output_path : Path) -> None:
    global jinja_env

    logging.info("Starting Jinja Env")
    try:
        jinja_env = Environment(loader=FileSystemLoader(templates_path))
    except Exception as e:
        logging.critical(f"Error initializing Jinja environment: {e}")
        raise e

    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.critical(f"Error creating output directory: {e}")
        raise e

    copy_static_files(static_path, output_path)
    process_markdown_files(content_path, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="RockyRacoon", description="Generate a website from markdown files")
    parser.add_argument("--root", "-r", default=".", help="Root directory, prepended to all other paths", type=Path)
    parser.add_argument("--content", "-i", default="content", help="Content directory with the markdown files", type=Path)
    parser.add_argument("--output", "-o", default="output", help="Output directory to store generated HTML files", type=Path)
    parser.add_argument("--static", "-s", default="static", help="Static directory for things like CSS files and images", type=Path)
    parser.add_argument("--templates", "-t", default="templates", help="Template directory for your Jinja templates", type=Path)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    args.content = args.root / args.content
    args.static = args.root / args.static
    args.templates = args.root / args.templates
    args.output = args.root / args.output

    logging.info("Checking directory paths are valid")
    for path in [args.root, args.content, args.static, args.templates]:
        if not path.exists() or not path.is_dir():
            error_msg = f"Path \"{path}\" doesn't exist"
            logging.critical(error_msg)
            sys.exit(1)

    logging.info("Starting RockyRacoon")

    try:
        generate_site(args.content, args.templates, args.static, args.output)
    except Exception as e:
        error_msg = f"Build failed: {e}"
        logging.critical(error_msg)
        sys.exit(1)

    logging.info("Build complete")
