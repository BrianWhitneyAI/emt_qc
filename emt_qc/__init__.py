# -*- coding: utf-8 -*-

"""Top-level package for emt_qc."""

__author__ = "Brian Whitney"
__email__ = "brian.whitney@alleninstitute.org"
# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "0.0.0"


def get_module_version():
    return __version__


from .example import Example  # noqa: F401
from .emt_block_duration import emt_block_duration, emt_block_qc_run_all

