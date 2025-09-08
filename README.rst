Typesense for Open edX (Tutor Plugin)
=======================================

This is a plugin for `Tutor <https://docs.tutor.edly.io>`_ 20 (Open edX "Teak" release) that provides Typesense to the platform, so it can be used as a search engine to power content search.

Installation
------------

Currently, you need to clone this repo from GitHub then install it into your tutor virtual environment with::

    pip install -e ./tutor-contrib-typesense

Then, to enable this plugin, run::

    tutor plugins enable typesense

If you have an already running platform, initialize this plugin with a command like the following::

    tutor [local|dev|k8s] do init --limit=typesense

Or use ``tutor [local|dev|k8s] launch -I`` to re-launch the platform (takes much longer).

Configuration
-------------

- ``TYPESENSE_COLLECTION_PREFIX`` (default: ``"tutor_"``)
- ``TYPESENSE_PUBLIC_HOST`` (default: ``"typesense.{{ LMS_HOST }}"``)
- ``TYPESENSE_DOCKER_IMAGE`` (default: ``"docker.io/typesense/typesense:29.0"``)
- ``TYPESENSE_BOOTSTRAP_API_KEY`` The initial admin API key to use when bootstrapping the Typesense server and to generate an api key for Open edX (default: auto-generated).
- ``TYPESENSE_API_KEY`` The API key used by Open edX (default: auto-generated).

These values can be modified with ``tutor config save --set PARAM_NAME=VALUE`` commands.

Limitations
-----------

It's not recommended to run high availability (clustered) Typesense on Kubernetes. See `typesense/typesense#465 <https://github.com/typesense/typesense/issues/465>` and `typesense/typesense#2049 <https://github.com/typesense/typesense/issues/2049>` for more information.

This plugin does not support deploying a clustered Typesense server.

Upgrading
---------
If you upgrade this plugin or change the ``TYPESENSE_DOCKER_IMAGE`` setting, you may get a new version of Typesense.
According to `Typesense docs on updating <https://typesense.org/docs/guide/updating-typesense.html#typesense-self-hosted>`_,
this upgrade happens automatically, and no manual actions are required.

DNS records
-----------

For production use, it is assumed that the ``TYPESENSE_PUBLIC_HOST`` DNS record points to your server.

In development mode, Typesense is available at http://typesense.local.openedx.io:8108.

Troubleshooting
---------------

TBD

Development
-----------

Set up a python virtual environment, then you can install dependencies and run the tests like:

  make install
  make test

After making some changes, you can run the auto formatter over the code for consistency:

  make format


Open edX integration
--------------------

This plugin provides the following settings to Open edX components for integration:

- (common) ``TYPESENSE_ENABLED: bool = True`` - whether the Typesense backend is enabled
- (common) ``TYPESENSE_COLLECTION_PREFIX: str = "the_configured_collection_prefix"`` - a prefix that the backend should use for all collections (the API key is scoped to this prefix)
- (common) ``FORUM_SEARCH_BACKEND = "forum.search.typesense.TypesenseBackend"`` - necessary to override Tutor's default forum search backend value pointing to Meilisearch
- (common) ``SEARCH_ENGINE = "search.typesense.TypesenseEngine"`` - necessary to override Tutor's default courseware search backend value pointing to Meilisearch
- (cms, lms) ``TYPESENSE_URLS: list[str] = ["http://typesense:8108"]`` - the internal urls for accessing the Typesense API.
- (cms, lms) ``TYPESENSE_PUBLIC_URL: str = "http://(depends on TYPESENSE_PUBLIC_HOST)"`` - the public url to the Typesense API (for user searches on the frontend)
- (cms, lms) ``TYPESENSE_API_KEY: str = "the api key"`` - an api key for the Open edX backend to make updates to Typesense collections
- (lms) ``MFE_CONFIG["TYPESENSE_ENABLED"]: bool = True`` - for MFE's to know when to use Typesense logic

License
-------

This work is licensed under the terms of the `GNU Affero General Public License (AGPL) <https://github.com/open-craft/tutor-contrib-typesense/blob/master/LICENSE.txt>`_.
