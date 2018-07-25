from datetime import datetime
import os
import sys


extensions = ["releases"]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
exclude_patterns = ["_build"]

project = u"pytest-relaxed"
year = datetime.now().year
copyright = u"%d Jeff Forcier" % year

# Ensure project directory is on PYTHONPATH for version, autodoc access
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

# Extension/theme settings
html_theme_options = {
    "description": "Relaxed pytest discovery",
    "github_user": "bitprophet",
    "github_repo": "pytest-relaxed",
    "fixed_sidebar": True,
}
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
        "donate.html",
    ]
}
# TODO: make it easier to configure this and alabaster at same time, jeez
releases_github_path = "bitprophet/pytest-relaxed"
