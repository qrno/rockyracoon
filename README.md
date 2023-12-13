# RockyRaccoon

A _tiny_ static site generator built in Python.

## Philosophy

This project seeks to do the bare minimum you need if you're not willing to write your website's raw HTML.

It has only two dependencies (for Markdown and templating) and a minimal codebase.

## Installation

Clone the repository and install the required dependencies:

```sh
git clone https://github.com/qrno/rockyracoon
pip install -r requirements.txt
```

## Usage

1. Templates:
   - Create [Jinja](https://palletsprojects.com/p/jinja/) teamplates and plcae them in the "templates/" directory.
   - A "default.html" template is provided and will be used if the markdown doesn't specify another one.
2. Markdown Files:
   - Put your markdown files in the "content/" directory.
   - You can create subdirectories; they will be properly reflected in the final output
3. Front Matter:
   - At the start of the markdown files, place a JSON object between two lines containing "---".
   - This data will be passed forward to your Jinja templates.
   - Use the "template" attribute to define which template should be used for the file.
4. Run the Generator:
    - Just run the main.py file to generate the website
    - Use the "--help" flag to check out all available flags
