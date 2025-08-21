import os
import secrets
from glob import glob
from pathlib import Path
from typing import Any, Literal

import importlib_resources
from tutor import hooks as tutor_hooks
from tutor.__about__ import __version_suffix__

from .__about__ import __version__

# Handle version suffix in nightly mode, just like tutor core
if __version_suffix__:
    __version__ += "-" + __version_suffix__

HERE = Path(__file__).resolve().parent

# Generate random master key and API key. Need to do this in python so we can compute the hash, which Jinja2 can't do.
# Note that this default will change every time, but that's fine. Once it's saved into the user's config it's stable.
random_bootstrap_api_key = secrets.token_urlsafe(32)
random_api_key = secrets.token_urlsafe(32)

config: dict[str, dict[str, Any]] = {
    "defaults": {
        "VERSION": __version__,
        # use a prefix to segregate data if you have multiple Open edX instances sharing one Typesense instance
        "COLLECTION_PREFIX": "tutor_",
        "PUBLIC_HOST": "typesense.{{ LMS_HOST }}",
        "DOCKER_IMAGE": "docker.io/typesense/typesense:29.0",
    },
    "unique": {
        # A key that we use during init to generate an API key, if required
        "BOOTSTRAP_API_KEY": random_bootstrap_api_key,
        # The API key that Open edX will use to connect
        "API_KEY": random_api_key,
    },
    "overrides": {
        # Override other Tutor settings using the above values, if needed.
    },
}

# Add configuration entries
tutor_hooks.Filters.CONFIG_DEFAULTS.add_items(
    [(f"TYPESENSE_{key}", value) for key, value in config.get("defaults", {}).items()]
)
tutor_hooks.Filters.CONFIG_UNIQUE.add_items(
    [(f"TYPESENSE_{key}", value) for key, value in config.get("unique", {}).items()]
)
tutor_hooks.Filters.CONFIG_OVERRIDES.add_items(
    list(config.get("overrides", {}).items())
)


@tutor_hooks.Filters.APP_PUBLIC_HOSTS.add()
def add_typesense_hosts(
    hosts: list[str], context_name: Literal["local", "dev"]
) -> list[str]:
    if context_name == "dev":
        hosts.append("{{ TYPESENSE_PUBLIC_HOST }}:8108")
    else:
        hosts.append("{{ TYPESENSE_PUBLIC_HOST }}")
    return hosts


# Add our init scripts:
SCRIPTS = HERE / "templates" / "typesense" / "tasks" / "typesense"
# This script will initialize Typesense by creating the API key used by edxapp:
tutor_hooks.Filters.CLI_DO_INIT_TASKS.add_item(
    ("typesense", (SCRIPTS / "init.sh").read_text()),
    priority=tutor_hooks.priorities.HIGH,
)

# TODO: enable this when the typesense backend for Open edX is ready.
# This script will create the Studio content index, and print
# instructions on how to reindex studio content, if needed.
# tutor_hooks.Filters.CLI_DO_INIT_TASKS.add_item(
#     ("cms", "./manage.py cms reindex_studio --experimental --init"),
#     priority=tutor_hooks.priorities.LOW,
# )

# Add the "templates" folder as a template root
tutor_hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    str(importlib_resources.files("tutor_typesense") / "templates")
)
# Render the "build" and "apps" folders
# tutor_hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
#     [
#         ("typesense/build", "plugins"),
#         ("typesense/apps", "plugins"),
#     ],
# )
# Load patches from files
for path in glob(str(importlib_resources.files("tutor_typesense") / "patches" / "*")):
    with open(path, encoding="utf-8") as patch_file:
        tutor_hooks.Filters.ENV_PATCHES.add_item(
            (os.path.basename(path), patch_file.read())
        )
