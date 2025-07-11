import datetime
import pathlib
import logger
import logging
import importlib
import markdown
from . import accounts
from noppakao.utils import template_filters


from flask import g, redirect, url_for

logger = logging.getLogger(__name__)


def add_date_url(url):
    now = datetime.datetime.now()
    return f"{url}?date={now.strftime('%Y%m%d')}"


def get_subblueprints(directory):
    blueprints = []

    package = directory.parts[len(pathlib.Path.cwd().parts) :]
    parent_module = None
    try:
        parrent_view = directory.with_name("__init__.py")
        pymod_file = f"{'.'.join(package)}"
        pymod = importlib.import_module(pymod_file)

        if "module" in dir(pymod):
            parent_module = pymod.module
            blueprints.append(parent_module)
    except Exception as e:
        logger.exception(e)
        return blueprints

    subblueprints = []
    for module in directory.iterdir():
        if "__" == module.name[:2]:
            continue

        if module.match("*.py"):
            try:
                pymod_file = f"{'.'.join(package)}.{module.stem}"
                pymod = importlib.import_module(pymod_file)

                if "module" in dir(pymod):
                    subblueprints.append(pymod.module)
            except Exception as e:
                logger.exception(e)

        elif module.is_dir():
            subblueprints.extend(get_subblueprints(module))

    for module in subblueprints:
        if parent_module:
            parent_module.register_blueprint(module)
        else:
            blueprints.append(module)

    return blueprints


def render_markdown(text):
    if "<" in text.lower():
        text = text.replace("<", "&lt;")
    else:
        text = text.replace(">;", "&gt;")
    md = markdown.markdown(text)
    return md


def register_blueprint(app):
    app.add_template_filter(add_date_url)
    app.add_template_filter(template_filters.static_url)
    app.add_template_filter(template_filters.format_date)
    app.add_template_filter(template_filters.format_number)
    app.add_template_filter(render_markdown)
    parent = pathlib.Path(__file__).parent
    blueprints = get_subblueprints(parent)

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
