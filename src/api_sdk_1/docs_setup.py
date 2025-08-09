# docs_setup.py
"""
Documentation Generation Setup for Agent Evaluation SDK

This script sets up and demonstrates multiple documentation generation approaches:
1. Sphinx (most comprehensive)
2. pdoc (simplest)
3. mkdocs with mkdocstrings (modern)
"""

import os
import sys
import subprocess
from pathlib import Path


# === SETUP SCRIPT ===

def setup_directories():
    """Create directory structure for documentation"""
    dirs = [
        "docs",
        "docs/source",
        "docs/build",
        "docs/api",
        "docs/guides",
        "docs/examples"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✅ Directory structure created")


def install_doc_tools():
    """Install documentation generation tools"""
    packages = [
        "sphinx",
        "sphinx-rtd-theme",
        "sphinx-autodoc-typehints",
        "pdoc",
        "mkdocs",
        "mkdocs-material",
        "mkdocstrings[python]",
        "black"  # For code formatting in docs
    ]

    print("Installing documentation tools...")
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print("✅ Documentation tools installed")


# === SPHINX CONFIGURATION ===

SPHINX_CONF = '''# docs/source/conf.py
"""Sphinx configuration for Agent Evaluation SDK"""

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# Project information
project = 'Agent Evaluation SDK'
copyright = '2024, Evaluation Platform Team'
author = 'Evaluation Platform Team'
release = '2.0.0'

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # Google/NumPy style docstrings
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx_autodoc_typehints',
]

# Extension settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Type hints
typehints_fully_qualified = False
always_document_param_types = True

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'requests': ('https://requests.readthedocs.io/en/master/', None),
}

# Theme
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False
}

# Static files
html_static_path = ['_static']
html_css_files = ['custom.css']

# Output
html_title = "Agent Evaluation SDK Documentation"
html_short_title = "Eval SDK"
html_logo = None
html_favicon = None
'''

SPHINX_INDEX = '''.. Agent Evaluation SDK documentation

Agent Evaluation SDK Documentation
===================================

Welcome to the Agent Evaluation SDK documentation!

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   quickstart
   installation
   authentication

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guides/basic_usage
   guides/advanced_features
   guides/best_practices

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/client
   api/agents
   api/evaluations
   api/results

.. toctree::
   :maxdepth: 1
   :caption: Examples

   examples/ci_integration
   examples/batch_processing
   examples/webhooks

API Documentation
-----------------

.. automodule:: agent_eval_sdk
   :members:
   :undoc-members:
   :show-inheritance:

Client
------

.. autoclass:: agent_eval_sdk.EvalClient
   :members:
   :undoc-members:
   :show-inheritance:

Models
------

.. autoclass:: agent_eval_sdk.Agent
   :members:
   :show-inheritance:

.. autoclass:: agent_eval_sdk.TestSuite
   :members:
   :show-inheritance:

.. autoclass:: agent_eval_sdk.Evaluation
   :members:
   :show-inheritance:

.. autoclass:: agent_eval_sdk.EvaluationResults
   :members:
   :show-inheritance:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
'''

SPHINX_QUICKSTART = '''Quickstart Guide
================

This guide will get you up and running with the Agent Evaluation SDK in 5 minutes.

Installation
------------

Install the SDK using pip::

    pip install agent-eval-sdk

Basic Usage
-----------

1. Import and initialize the client::

    from agent_eval_sdk import EvalClient

    client = EvalClient(api_key="your_api_key")

2. Create an agent::

    agent = client.agents.create(
        name="My Agent",
        model="gpt-4"
    )

3. Run an evaluation::

    evaluation = client.evaluations.create(
        agent_id=agent.id,
        test_suite_id="suite_001"
    )

    results = evaluation.wait_for_completion()
    print(f"Score: {results.overall_score}")

Quick Evaluation
----------------

For rapid testing, use the convenience method::

    results = client.quick_evaluate(
        agent_name="Test Agent",
        agent_model="gpt-4"
    )

Next Steps
----------

- Read the :doc:`guides/basic_usage` for detailed examples
- Explore :doc:`api/client` for complete API reference
- Check out :doc:`examples/ci_integration` for CI/CD integration
'''

# === MKDOCS CONFIGURATION ===

MKDOCS_CONFIG = '''# mkdocs.yml
site_name: Agent Evaluation SDK
site_description: Python SDK for AI Agent Evaluation Platform
site_author: Evaluation Platform Team
site_url: https://docs.eval.ai

repo_name: eval-ai/python-sdk
repo_url: https://github.com/eval-ai/python-sdk
edit_uri: edit/main/docs/

theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

  features:
    - navigation.instant
    - navigation.tracking
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.sections
    - navigation.expand
    - navigation.path
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy
    - content.code.annotate

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            show_source: true
            show_signature_annotations: true
            show_if_no_docstring: false
            inherited_members: true
            members_order: source
            separate_signature: true
            unwrap_annotated: true
            filters: ["!^_"]
            merge_init_into_class: true
            docstring_section_style: spacy

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - admonition
  - pymdownx.details
  - pymdownx.emoji:
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
  - attr_list
  - md_in_html

nav:
  - Home: index.md
  - Getting Started:
      - Installation: getting-started/installation.md
      - Quickstart: getting-started/quickstart.md
      - Authentication: getting-started/authentication.md
  - User Guide:
      - Basic Usage: guide/basic-usage.md
      - Advanced Features: guide/advanced-features.md
      - Best Practices: guide/best-practices.md
  - API Reference:
      - Client: api/client.md
      - Agents: api/agents.md
      - Evaluations: api/evaluations.md
      - Models: api/models.md
  - Examples:
      - CI/CD Integration: examples/ci-integration.md
      - Batch Processing: examples/batch-processing.md
      - Webhooks: examples/webhooks.md
  - Changelog: changelog.md

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/eval-ai
    - icon: fontawesome/brands/discord
      link: https://discord.gg/eval
    - icon: fontawesome/brands/twitter
      link: https://twitter.com/eval_ai
'''

MKDOCS_INDEX = '''# Agent Evaluation SDK

Welcome to the official Python SDK documentation for the AI Agent Evaluation Platform!

## What is this SDK?

The Agent Evaluation SDK provides a simple, powerful interface to evaluate AI agents against standardized test suites. Whether you're building LLMs, conversational agents, or autonomous systems, our SDK helps you measure and improve performance.

## Quick Example

```python
from agent_eval_sdk import EvalClient

# Initialize client
client = EvalClient(api_key="your_api_key")

# Quick evaluation
results = client.quick_evaluate(
    agent_name="My Agent",
    agent_model="gpt-4"
)

print(f"Score: {results.overall_score:.1%}")
```

## Key Features

- 🚀 **Simple API** - Get started in minutes
- 📊 **Comprehensive Metrics** - Detailed performance breakdowns
- ⚡ **Async Support** - Non-blocking evaluation runs
- 🔄 **CI/CD Ready** - Perfect for automation
- 📈 **Progress Tracking** - Real-time status updates
- 🪝 **Webhooks** - Event-driven notifications

## Installation

=== "pip"

    ```bash
    pip install agent-eval-sdk
    ```

=== "poetry"

    ```bash
    poetry add agent-eval-sdk
    ```

=== "requirements.txt"

    ```text
    agent-eval-sdk>=2.0.0
    ```

## Next Steps

- [Quickstart Guide](getting-started/quickstart.md) - Get running in 5 minutes
- [API Reference](api/client.md) - Complete API documentation  
- [Examples](examples/ci-integration.md) - Real-world use cases

## Need Help?

- 📚 Check our [User Guide](guide/basic-usage.md)
- 💬 Join our [Discord Community](https://discord.gg/eval)
- 🐛 Report issues on [GitHub](https://github.com/eval-ai/python-sdk/issues)
'''

MKDOCS_API_CLIENT = '''# Client API Reference

::: agent_eval_sdk.EvalClient
    options:
      show_source: true
      show_signature_annotations: true
      members:
        - __init__
        - quick_evaluate
        - health_check
      heading_level: 2

## Sub-APIs

The client provides access to specialized APIs through these attributes:

### agents

::: agent_eval_sdk.AgentsAPI
    options:
      show_source: false
      heading_level: 3

### evaluations  

::: agent_eval_sdk.EvaluationsAPI
    options:
      show_source: false
      heading_level: 3

### test_suites

::: agent_eval_sdk.TestSuitesAPI
    options:
      show_source: false
      heading_level: 3

### webhooks

::: agent_eval_sdk.WebhooksAPI
    options:
      show_source: false
      heading_level: 3

## Utility Functions

::: agent_eval_sdk.get_client_from_env
    options:
      show_source: true
      heading_level: 3
'''

# === PDOC CONFIGURATION ===

PDOC_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ module.name }} - Agent Evaluation SDK</title>
    <style>
        /* Custom styling for better appearance */
        body { font-family: system-ui, -apple-system, sans-serif; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        code { background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }
        pre { background: #f8f8f8; padding: 1em; border-radius: 5px; }
        .module { margin-bottom: 2em; }
        .class { border-left: 3px solid #667eea; padding-left: 1em; }
        .function { border-left: 3px solid #764ba2; padding-left: 1em; }
    </style>
</head>
<body>
    {{ content }}
</body>
</html>
'''


# === GENERATION SCRIPTS ===

def generate_sphinx_docs():
    """Generate documentation using Sphinx"""
    print("\n📚 Generating Sphinx Documentation...")

    # Write configuration files
    with open("docs/source/conf.py", "w") as f:
        f.write(SPHINX_CONF)

    with open("docs/source/index.rst", "w") as f:
        f.write(SPHINX_INDEX)

    with open("docs/source/quickstart.rst", "w") as f:
        f.write(SPHINX_QUICKSTART)

    # Initialize Sphinx project if needed
    if not Path("docs/source/Makefile").exists():
        subprocess.run(["sphinx-quickstart", "docs/source", "--quiet",
                        "--project=Agent Evaluation SDK",
                        "--author=Team", "-v=2.0.0", "--makefile"])

    # Build HTML documentation
    subprocess.run(["sphinx-build", "-b", "html", "docs/source", "docs/build/html"])

    print("✅ Sphinx docs generated at: docs/build/html/index.html")
    print("   View with: python -m http.server 8000 --directory docs/build/html")


def generate_pdoc_docs():
    """Generate documentation using pdoc"""
    print("\n📚 Generating pdoc Documentation...")

    # Generate HTML documentation
    subprocess.run(["pdoc", "--html", "--output-dir", "docs/pdoc",
                    "--config", "show_source_code=True",
                    "--config",
                    "git_link_template='https://github.com/eval-ai/python-sdk/blob/main/{path}#L{start_line}-L{end_line}'",
                    "agent_eval_sdk"])

    print("✅ pdoc docs generated at: docs/pdoc/agent_eval_sdk.html")
    print("   View with: python -m http.server 8001 --directory docs/pdoc")


def generate_mkdocs_docs():
    """Generate documentation using MkDocs"""
    print("\n📚 Generating MkDocs Documentation...")

    # Write configuration
    with open("mkdocs.yml", "w") as f:
        f.write(MKDOCS_CONFIG)

    # Create docs directory structure
    Path("docs/getting-started").mkdir(parents=True, exist_ok=True)
    Path("docs/guide").mkdir(parents=True, exist_ok=True)
    Path("docs/api").mkdir(parents=True, exist_ok=True)
    Path("docs/examples").mkdir(parents=True, exist_ok=True)

    # Write index
    with open("docs/index.md", "w") as f:
        f.write(MKDOCS_INDEX)

    # Write API reference page
    with open("docs/api/client.md", "w") as f:
        f.write(MKDOCS_API_CLIENT)

    # Build the documentation
    subprocess.run(["mkdocs", "build"])

    print("✅ MkDocs docs generated at: site/index.html")
    print("   Serve live with: mkdocs serve")


# === COMPARISON SCRIPT ===

def compare_generators():
    """Generate comparison of different documentation tools"""

    comparison = """
# Documentation Generator Comparison

## 1. Sphinx (Classic & Comprehensive)
   ✅ Pros:
   - Industry standard for Python projects
   - Extensive customization options
   - Great for large projects
   - Supports multiple output formats (HTML, PDF, ePub)
   - Rich extension ecosystem

   ❌ Cons:
   - Steeper learning curve
   - reStructuredText can be less intuitive
   - More configuration required

## 2. pdoc (Simple & Fast)
   ✅ Pros:
   - Zero configuration needed
   - Fast generation
   - Clean, simple output
   - Supports Markdown in docstrings

   ❌ Cons:
   - Less customization
   - Fewer features
   - No multi-page navigation

## 3. MkDocs (Modern & Beautiful)
   ✅ Pros:
   - Beautiful Material theme
   - Markdown-based
   - Great search functionality
   - Live reload during development
   - Good for mixing auto-generated and manual docs

   ❌ Cons:
   - Requires more manual content creation
   - mkdocstrings plugin needed for auto-generation

## Recommendation:
- **For your use case**: MkDocs with mkdocstrings
  - Modern, beautiful output
  - Good balance of automation and control
  - Excellent developer experience
  - Easy to integrate custom guides with auto-generated API docs
"""

    print(comparison)

    # Write comparison to file
    with open("docs/comparison.md", "w") as f:
        f.write(comparison)


# === MAIN EXECUTION ===

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate SDK documentation")
    parser.add_argument("--tool", choices=["sphinx", "pdoc", "mkdocs", "all", "compare"],
                        default="all", help="Documentation tool to use")
    parser.add_argument("--setup", action="store_true",
                        help="Install required packages")

    args = parser.parse_args()

    if args.setup:
        setup_directories()
        install_doc_tools()

    if args.tool == "sphinx" or args.tool == "all":
        generate_sphinx_docs()

    if args.tool == "pdoc" or args.tool == "all":
        generate_pdoc_docs()

    if args.tool == "mkdocs" or args.tool == "all":
        generate_mkdocs_docs()

    if args.tool == "compare" or args.tool == "all":
        compare_generators()

    print("\n🎉 Documentation generation complete!")
    print("\nQuick commands:")
    print("  Sphinx:  python -m http.server 8000 --directory docs/build/html")
    print("  pdoc:    python -m http.server 8001 --directory docs/pdoc")
    print("  MkDocs:  mkdocs serve")
