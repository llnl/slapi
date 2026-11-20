# SLAPI

SLAPI is a command-line tool that communicates with Spectra Logic tape
libraries using their LumOS REST API.  This provides a simple way to
administer and monitor Spectra Logic tape libraries in large data centers.

Prerequisites
----------------

Build requirements for SLAPI are:
```bash
python 3.11+
java 25 OpenJDK
automake
quilt
curl
```

Getting Started
----------------

    $ make
    $ pip install src/lumosapi_client -r src/requirements.txt

SLAPI binary will be generated in `src/slapi`.

Configuration files
----------------

Unless overridden by `--config`, SLAPI will pick up a system-wide configuration file in `/etc/slapi.conf` or a user-specific configuration file in `~/.slapi/slapi.conf`.

The configuration file is a simple INI file. If you specify `--server`, the section with that exact same name will be read; if you do not specify a server, the `[DEFAULT]` section will be read instead and the `server` key in that section will be used. Do not specify `server` in named sections; it will not override what you pass on the CLI.

Keys that are not specified in named sections will fall back to the key in `[DEFAULT]` if present there.

The following keys are supported in each section:
| Key      | Notes |
| -------- | ----- |
| server   | Does NOT override `--server`, so it's best to not specify this outside of `[DEFAULT]`. |
| port     | |
| insecure | true or false. Communicate with library over http:// instead of https:// |
| username | On CLI, this is `--user` |
| password | Allowed to be empty (but the key must still be present). The escape character is `%`, so a percent sign in your password will need to be escaped as `%%`. |
| verbose  | true or false. |

Comments are allowed, the comment prefix is `#`.

Here is a sample configuration file with two libraries:

``` INI
[DEFAULT]
server = tfinity01.mydomain.com
username = su
# % escaped as %%
password = ThisPwdHasOnlyOne%%.
verbose = false
insecure = true

[theoneweneveruse.mydomain.com]
username = su
password = supersecret!
```

Documentation
----------------

Currently the documentation for SLAPI is provided with the help option.

    $ ./slapi --help

Contributing
----------------
See CONTRIBUTING.md


Release
----------------

SPDX-License-Identifier: GPL-2.0-or-later

LLNL-CODE-769480
