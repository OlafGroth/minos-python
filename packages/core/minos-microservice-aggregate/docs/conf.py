import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(".."))

from minos import (
    aggregate as module,
)

extensions = [
    "sphinxcontrib.apidoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx_rtd_theme",
    "m2r2",
]
templates_path = ["_templates"]
source_suffix = [".rst", ".md"]

master_doc = "index"
project = "minos-microservice-aggregate"
copyright = f"2021-{datetime.now().year}, Clariteia"
author = "Minos Framework Devs"

version = module.__version__
release = module.__version__

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

pygments_style = "sphinx"

todo_include_todos = False
html_theme = "sphinx_rtd_theme"
html_sidebars = {"**": ["about.html", "navigation.html", "searchbox.html"]}
html_static_path = ["_static"]
htmlhelp_basename = "minosdoc"

apidoc_module_dir = "../minos"
apidoc_output_dir = "api"
apidoc_toc_file = False
apidoc_separate_modules = True
apidoc_extra_args = [
    "--force",
    "--implicit-namespaces",
    "--templatedir=_templates",
]
autodoc_default_options = {
    "members": True,
    "inherited-members": True,
    "undoc-members": True,
    'member-order': 'bysource',
}
autoclass_content = "both"
autodoc_member_order = "bysource"
autodoc_typehints_format = "short"
autodoc_typehints = "description"
