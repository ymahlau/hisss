# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import tomllib
from pathlib import Path

# -- Project information -----------------------------------------------------

# Define path to pyproject.toml (assuming conf.py is in docs/source/)
root_path = Path(__file__).parents[2]

with open(root_path / "pyproject.toml", "rb") as f:
    data = tomllib.load(f)

project = data["project"]["name"]  # Or keep hardcoded if you prefer formatting
author = data["project"]["authors"][0]["name"]  # Auto-fetch author
release = data["project"]["version"]

copyright = f"2026, {author}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "myst_nb",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_favicon = "_static/favicon.ico"
html_logo = "_static/drinx_text.svg"

html_theme_options = {
    "repository_url": "https://github.com/ymahlau/drinx",
    "repository_branch": "main",  # or "master" if that's your default branch
    "use_repository_button": True,  # This enables the repository button
}

napoleon_google_docstring = True
autosummary_generate = True
# Set to 'separated' to display signature as a method instead of in the class header
# autodoc_class_signature = 'separated'
# autodoc_typehints = 'signature'

# autodoc_default_options = {
#     'exclude-members': '__init__, __new__, __post_init__, __repr__, __eq__, __hash__, __weakref__',
#     'undoc-members': False,  # Don't document members without docstrings
# }

autodoc_default_options = {
    "undoc-members": False,  # Don't document members without docstrings
}

nb_execution_mode = "off"

myst_enable_extensions = [
    "amsmath",
    "dollarmath",
]

# MathJax configuration (optional, for customization)
mathjax3_config = {
    "tex": {
        "inlineMath": [["$", "$"], ["\\(", "\\)"]],
        "displayMath": [["$$", "$$"], ["\\[", "\\]"]],
    }
}
