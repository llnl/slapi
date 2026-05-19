# SLAPI

SLAPI is a command-line tool that communicates with Spectra Logic tape
libraries using their LumOS REST API.  This provides a simple way to
administer and monitor Spectra Logic tape libraries in large data centers.

Getting Started
----------------

In order to use SLAPI, you must have python3.11 installed on your system.

    $ make
    $ cd src/lumosapi_client
    $ python3.11 setup.py bdist_wheel
    $ pip3.11 install dist/lumosapi_client-3.0.1-py3-none-any.whl
    $ pip3.11 install --upgrade requests urllib3 pandas

Documentation
----------------

Currently the documentation for SLAPI is provided with the help option.

    $ slapi --help

Contributing
----------------
See CONTRIBUTING.md


Release
----------------

SPDX-License-Identifier: GPL-2.0-or-later

LLNL-CODE-769480
