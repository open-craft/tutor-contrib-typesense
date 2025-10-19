import os
import secrets
from glob import glob
from pathlib import Path
from typing import Literal

import importlib_resources
from tutor import hooks
from tutor.__about__ import __version_suffix__

from .__about__ import __version__

# Handle version suffix in nightly mode, just like tutor core
if __version_suffix__:
    __version__ += "-" + __version_suffix__

HERE = Path(__file__).resolve().parent

hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        ("TYPESENSE_COLLECTION_PREFIX", "tutor_"),
        ("TYPESENSE_PUBLIC_HOST", "typesense.{{ LMS_HOST }}"),
        ("TYPESENSE_DOCKER_IMAGE", "docker.io/typesense/typesense:29.0"),
        ("TYPESENSE_VOLUME_SIZE", "5Gi"),
    ]
)

hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        ("TYPESENSE_BOOTSTRAP_API_KEY", secrets.token_urlsafe(32)),
        ("TYPESENSE_API_KEY", secrets.token_urlsafe(32)),
    ]
)


@hooks.Filters.APP_PUBLIC_HOSTS.add()
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
hooks.Filters.CLI_DO_INIT_TASKS.add_item(
    ("typesense", (SCRIPTS / "init.sh").read_text()),
    priority=hooks.priorities.HIGH,
)

# TODO: enable this when the typesense backend for Open edX is ready.
# This script will create the Studio content index, and print
# instructions on how to reindex studio content, if needed.
# hooks.Filters.CLI_DO_INIT_TASKS.add_item(
#     ("cms", "./manage.py cms reindex_studio --experimental --init"),
#     priority=hooks.priorities.LOW,
# )

# Add the "templates" folder as a template root
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    str(importlib_resources.files("tutor_typesense") / "templates")
)

# Load patches from files
for path in glob(str(importlib_resources.files("tutor_typesense") / "patches" / "*")):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))
