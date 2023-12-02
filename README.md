# RockyRacoon - Tiny Static Site Generator in Python

## Installation

Clone the repository and run the following command
to install the program's dependencies.

```
pip install -r requirements.txt
```


## Usage

Create jinja templates and place them in the "templates/" directory.

Write your markdown files in the "content/" directory.
Feel free to create subdirectories inside of that folder,
they will be appropriately reflected in the final output.

At the start of the markdown files you can put a json object
between two lines containing "---" and that data will be passed
forward to your jinja templates.
A special attribute you can define is "template",
which defines which of your templates should be used for the file.
