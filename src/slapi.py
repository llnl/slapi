#!/usr/bin/env python3.8
#
# Copyright (C) 2019 Lawrence Livermore National Security, LLC
# Please see top-level LICENSE for details.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import getpass
import functools
import sys
import os
import stat
import time
import pathlib
import configparser
import requests
import logging
import urllib.request
import urllib.error
import http.cookiejar
import platform
import ssl
import json
import xml.etree.ElementTree
import xml.dom.minidom
import traceback
import datetime
import re

class SpectraLogicLoginError(Exception):

    LoginErrorRaised = False

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class IncompatibleParameterError(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class TLSAdapter(requests.adapters.HTTPAdapter):

    #--------------------------------------------------------------------------
    #
    def __init__(self, **kwargs):
        super(TLSAdapter, self).__init__(**kwargs)

    #--------------------------------------------------------------------------
    #
    def init_poolmanager(self, *pool_args, **pool_kwargs):
        context = ssl._create_unverified_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        context.options = ssl.PROTOCOL_TLS & ssl.OP_NO_TLSv1 & ssl.OP_NO_TLSv1_1
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        self.poolmanager = requests.packages.urllib3.poolmanager.PoolManager(ssl_context=context)

class SpectraLogicAPI:

    #--------------------------------------------------------------------------
    #
    def __init__(self, args):
        self.server            = args.server
        self.port              = args.port
        self.user              = args.user
        self.passwd            = args.passwd
        self.verbose           = args.verbose
        self.insecure          = args.insecure
        self.longlist          = args.longlist
        self.loggedin          = False
        self.token             = ""
        self.tokenexpiresat    = -1
        self.refreshuntil      = -1
        self.session           = requests.session()
        self.sessionid         = ""
        self.cookiefile        = self.slapi_directory() + "/cookies_lumos.txt"
        self.load_cookie()
        if args.insecure == False:
            httpstr = "https://"
            self.adapter = TLSAdapter()
        else:
            httpstr = "http://"
            self.adapter = HTTPAdapter()
        self.baseurl = httpstr + args.server + "/api"
        self.session.mount(httpstr, self.adapter)
        if args.port is not None:
            self.baseurl = httpstr + args.server + ":" + str(args.port) + "/api"

    #--------------------------------------------------------------------------
    #
    def __str__(self):
        return(f"Server:        {self.server}\n"
               f"Port:          {self.port}\n"
               f"Username:      {self.user}\n"
               f"Password:      ****\n"
               f"Verbose:       {self.verbose}\n"
               f"Insecure:      {self.insecure}\n"
               f"Long List:     {self.longlist}\n"
               f"Logged In:     {self.loggedin}\n"
               f"Token:         {self.token}\n"
               f"Expires At:    {datetime.datetime.fromtimestamp(self.tokenexpiresat)}\n"
               f"Refresh Until: {datetime.datetime.fromtimestamp(self.refreshuntil)}\n")
    #--------------------------------------------------------------------------
    #
    def slapi_directory(self):

        home = os.path.expanduser('~')
        if os.path.exists(home) == False:
            raise(Exception(home + " does not exist."))
        if os.path.isdir(home) == False:
            raise(Exception(home + " is not a directory."))

        slapidir = home + "/.slapi"
        if os.path.exists(slapidir):
            if os.path.isdir(slapidir):
                return(slapidir)
            else:
                raise(Exception(slapidir + " is not a directory."))
        else:
            # Directory does not exist
            # Let's try to create it
            try:
                os.mkdir(slapidir, 0o700)
                return(slapidir)
            except OSError as e:
                raise(e)


    #--------------------------------------------------------------------------
    #
    def cookie_is_old(self):

        try:
            now   = time.time()
            mtime = os.stat(self.cookiefile)[stat.ST_MTIME]
            age   = now - mtime
            if age < 3600:
                return(False)
            else:
                return(True)

        except Exception as e:
            return(True)

    #--------------------------------------------------------------------------
    #
    # Creates a string of xml output as a one item per line hierarchy.
    # Similar to long_listing but going to a string instead of printing.
    # Helpful for XML error markup.
    #
    def get_all_text(self, element, inputString):

        # add the name of the element
        outputString = inputString

        # add the text of the element; "None" if no text
        # if the tag is a line, then just print out the line.
        if element.text:
            if element.tag != "line":
                outputString = outputString + element.tag + ": " + element.text.rstrip()
            else:
                outputString = outputString + element.text.rstrip()
        else:
            if element.tag != "line":
                outputString = outputString + element.tag + ": None"
            else:
                outputString =  outputString + ": None"
        outputString = outputString + "\n"

        # recurse to the next level of elements
        for subelem in element:
            outputString = self.get_all_text(subelem, outputString)

        return(outputString)


    #--------------------------------------------------------------------------
    #
    def clear_cookie(self):
        try:
            tmpserver = self.server
            if tmpserver.find(".") == -1:
                tmpserver = tmpserver + ".local"
            for cookie in self.session.cookies:
                if cookie.domain == tmpserver:
                    self.session.cookies.clear(cookie.domain)
        except Exception as e:
            self.loggedin       = False
            self.sessionid      = ""
            self.token          = ""
            self.tokenexpiresat = -1
            self.refreshuntil   = -1


    #--------------------------------------------------------------------------
    #
    def load_cookie(self):

        try:
            tmpserver = self.server
            if tmpserver.find(".") == -1:
                tmpserver = tmpserver + ".local"
            lwp_cookiejar = http.cookiejar.LWPCookieJar()
            lwp_cookiejar.load(self.cookiefile, ignore_discard=True, ignore_expires=False)

            for cookie in lwp_cookiejar:
                if cookie.domain == tmpserver and cookie.name == "Authorization":
                    match = re.search("\"Bearer\s+(.*?)\"", cookie.value)
                    self.token = match.group(1)
                    self.loggedin = True

        except Exception as e:
            self.save_cookies()
            self.loggedin       = False
            self.sessionid      = ""
            self.token          = ""
            self.tokenexpiresat = -1
            self.refreshuntil   = -1

    #--------------------------------------------------------------------------
    #
    def save_cookies(self):
        try:
            os.umask(0o077)
            lwp_cookiejar = http.cookiejar.LWPCookieJar()
            for cookie in self.session.cookies:
                lwp_cookiejar.set_cookie(cookie)
            lwp_cookiejar.save(self.cookiefile, ignore_discard=True, ignore_expires=False)
        except Exception as e:
            os.umask(0o077)
            self.loggedin       = False
            self.sessionid      = ""
            self.token          = ""
            self.tokenexpiresat = -1
            self.refreshuntil   = -1


    #--------------------------------------------------------------------------
    #
    # Prints xml output as a one item per line hierarchy. Similar to XML output,
    # but without all the XML markup.
    #
    def long_listing(self, element, level):

        # add two spaces for each level
        for i in range(level):
            print("  ", end='')

        # print the name of the element
        print(element.tag, end='')

        # print the text of the element; "None" if no text
        if element.text:
            print(": " + element.text.rstrip())
        else:
            print(": None")

        # recurse to the next level of elements
        for subelem in element:
            self.long_listing(subelem, (level+1))

        sys.stdout.flush()


    #--------------------------------------------------------------------------
    #
    # This routine pretty prints the XML document to stderr if the verbose
    # flag is on.
    #
    def print_json_document(self, jsonstr):

        if self.verbose:
            print("--------------------------------------------------", file=sys.stderr)
            print("JSON Object:", file=sys.stderr)
            jsonobj = json.loads(jsonstr)
            json_pretty_str = json.dumps(jsonobj, indent=2)
            json_lines = json_pretty_str.splitlines()
            for line in json_lines:
                line = line.rstrip()
                if line != "":
                    print(line, file=sys.stderr)
            print("--------------------------------------------------", file=sys.stderr)
            print("", file=sys.stderr)


    #--------------------------------------------------------------------------
    #
    # Runs the REST API command
	# Return either JSON object by default, or the data as a string if
	# the returnstring parameter is set to True.
    #
    def run_command(self, url, params=None, post=False, returnstring=False):

        try:

            if self.verbose:
                tmpurl = url.replace(self.passwd, "*" * len(self.passwd))
                print("--------------------------------------------------", file=sys.stderr)
                print("Command: " + tmpurl, file=sys.stderr)
                print("--------------------------------------------------", file=sys.stderr)
                print("", file=sys.stderr)

            try:

                headers   = { "Content-Type": "application/json", "Authorization": f"Bearer {self.token}" }

                if post:
                    response  = self.session.post(url, json=params, headers=headers, verify=False, allow_redirects=True)
                else:
                    response  = self.session.get(url, headers=headers, verify=False, allow_redirects=True)
                jsonstr   = response.text
            except Exception as e:
                raise(e)

            # If we got an error from running the command, then we will be able
            # to successfully put into a tree and check for error records.
            checkerror = True
            if returnstring:
                checkerror = False

            try:
                jsonobj    = json.loads(jsonstr)
                checkerror = True

                # Pretty print the XML document if verbose on
                self.print_json_document(jsonstr)

            except Exception as e:

                if returnstring:
                    # It's okay if we couldn't turn the xmldoc into a tree; means
                    # we've got some good binary data
                    checkerror = False
                else:
                    raise(e)

            # check_for_error will raise an exception if it encounters a problem
            try:
                if checkerror:
                    self.check_for_error(jsonobj)

                if returnstring:
                    return(jsonstr)
                else:
                    return(jsonobj)

            except SpectraLogicLoginError as e:
                try:
                    if (self.verbose):
                        print("Loginerror: Raised: " +
                            str(SpectraLogicLoginError.LoginErrorRaised),
                            file=sys.stderr)

                    # If we haven't already had a login error, then login
                    # and retry the command
                    if SpectraLogicLoginError.LoginErrorRaised == False:
                        SpectraLogicLoginError.LoginErrorRaised = True
                        if (self.verbose):
                            print("Re-issuing login", file=sys.stderr)
                        self.login()
                        if (self.verbose):
                            print("Re-running command", file=sys.stderr)
                            return(self.run_command(url, params=params, post=post, returnstring=returnstring))
                    else:
                        raise(e)
                except Exception as e:
                    raise(e)
            except Exception as e:
                raise(e)

        except ConnectionRefusedError as e:
            print("Connection refused: " + str(e), file=sys.stderr)
            sys.exit(1)
        except urllib.error.URLError as e:
            if str(e.reason) == str('[Errno 111] Connection refused'):
                print("URL Error: " + str(e), file=sys.stderr)
                sys.exit(1)
            raise(e)
        except Exception as e:
            raise(e)

    #==========================================================================
    # DEFINE COMMAND FUNCTIONS
    #==========================================================================


    #--------------------------------------------------------------------------
    #
    # Checks for system error ("error" record) or syntax error ("syntaxError"
    # record) and raises an exception if it found any; otherwise it returns
    # false. The exception will contain the system/syntax error message.
    #
    # Raises the following exceptions:
    # - Exception: system/syntax error
    # - SpectraLogicLoginError: no active session found
    #
    def check_for_error(self, jsonobj):

        try:
            # If there aren't any records, then no errors
            if len(jsonobj) == 0:
                return(False)

            # Check for system error
            if "error" in jsonobj:
                errstr = ""
                if self.loggedin == False:
                    raise(SpectraLogicLoginError("Error: No active session found."))
                if "message" in jsonobj["error"]:
                    errstr = jsonobj["error"]["message"]
                raise(Exception(errstr))

        except SpectraLogicLoginError as e:
            raise(e)

        except Exception as e:
            if (self.verbose):
                print("check_for_error Error: " + str(e), file=sys.stderr)
                traceback.print_exc()
            raise(e)

        return(False)

    def frus(self):

        try:
            # FIXME for now force a login
            self.login()

            url     = self.baseurl + "/frus"
            params = dict()
            jsonobj = self.run_command(url, params=params, post=False)

            for key in jsonobj:
                fruobjs = jsonobj["value"]
                for fruobj in fruobjs:
                    frustatus = None
                    if "name" in fruobj:
                        url = self.baseurl + f"/frus/{fruobj['name']}/status"
                        params = dict()
                        frustatus = self.run_command(url, params=params, post=False)
                    self.print_fru_status(fruobj, frustatus)

        except Exception as e:
            raise(e)

    def inventory(self):

        try:
            # FIXME for now force a login
            self.login()

            url    = self.baseurl + "/inventory"
            params = dict()
            jsonobj = self.run_command(url, params=params, post=False)

        except Exception as e:
            raise(e)

    def librarystatus(self):

        try:
            url    = self.baseurl + "/library/status"
            params = dict()
            jsonobj = self.run_command(url, params=params, post=False)

        except Exception as e:
            raise(e)

    #--------------------------------------------------------------------------
    #
    # Connects to the library using the specified username and password. See
    # "Configuring Library Users" in your library User Guide for information
    # about configuring users and passwords, as well as information about what
    # sort of actions each user type can perform.
    #
    def login(self):

        try:
            url    = self.baseurl + "/auth/login"
            params = dict()
            params["domain"] = "NATIVE"
            params["username"] = self.user
            params["password"] = self.passwd
            jsonobj = self.run_command(url, params=params, post=True)

            for key in jsonobj:
                if key.casefold() == "error".casefold():
                    if jsonobj["error"]["code"] == 401:
                        print("Login Failed...\n", file=sys.stderr)
                        self.loggedin       = False
                        self.sessionid      = ""
                        self.token          = ""
                        self.tokenexpiresat = -1
                        self.refreshuntil   = -1
                        self.clear_cookie()
                        self.save_cookies()
                        break
                if key.casefold() == "passwordHasExpired".casefold():
                    if jsonobj[key] == True:
                        self.loggedin       = False
                        self.sessionid      = ""
                        self.token          = ""
                        self.tokenexpiresat = -1
                        self.refreshuntil   = -1
                        self.clear_cookie()
                        self.save_cookies()
                        break
                if key.casefold() == "refreshUntil".casefold():
                    self.refreshuntil = int(jsonobj[key])
                    continue
                if key.casefold() == "token".casefold():
                    self.token = jsonobj[key]
                    continue
                if key.casefold() == "tokenExpiresAt".casefold():
                    self.tokenexpiresat = int(jsonobj[key])
                    continue

            print(self)
            self.save_cookies()

        except Exception as e:
            raise(e)

    def spec(self):

        try:
            # FIXME for now force a login
            self.login()

            url    = self.baseurl + "/spec"
            params = dict()
            yamlstr = self.run_command(url, params=params, post=False, returnstring=True)

            print(f"{yamlstr}")

        except Exception as e:
            raise(e)

    def print_fru_status(self, fruobj, frustatus):

        for key in fruobj:
            if key.casefold() == "actions".casefold():
                next
            if key.casefold() == "type".casefold():
                if fruobj["type"].casefold() == "CAN_OVER_POWER".casefold():
                    pass
                elif fruobj["type"].casefold() == "DRIVE".casefold():
                    pass
                elif fruobj["type"].casefold() == "EXPORT_CONTROL_MODULE".casefold():
                    pass
                elif fruobj["type"].casefold() == "FRAME_CONTROL_MODULE".casefold():
                    pass
                elif fruobj["type"].casefold() == "FRAME_MANAGEMENT_MODULE".casefold():
                    pass
                elif fruobj["type"].casefold() == "LS".casefold():
                    pass
                elif fruobj["type"].casefold() == "NETWORK_SWITCH".casefold():
                    pass
                elif fruobj["type"].casefold() == "POWER_CONTROL_MODULE".casefold():
                    pass
                elif fruobj["type"].casefold() == "POWER_SUPPLY".casefold():
                    pass
                elif fruobj["type"].casefold() == "ROBOT".casefold():
                    pass
                elif fruobj["type"].casefold() == "SERVICE_CONTROL_MODULE".casefold():
                    pass
                elif fruobj["type"].casefold() == "PMM".casefold():
                    pass
                elif fruobj["type"].casefold() == "FMM".casefold():
                    pass
                elif fruobj["type"].casefold() == "FCM".casefold():
                    pass
                elif fruobj["type"].casefold() == "CAN_REPEATER".casefold():
                    pass
                elif fruobj["type"].casefold() == "ROBOTICS_INTERFACE_MODULE".casefold():
                    pass
            print(f"Key: {key} Value: {fruobj[key]}")
        print("")

    #--------------------------------------------------------------------------
    #
    # Closes the connection to the library.
    #
    def logout(self):

        try:
            url  = self.baseurl + "/logout.xml"
            tree = self.run_command(url)

        except Exception as e:
            print("Logout Error: " + str(e), file=sys.stderr)

        self.loggedin       = False
        self.sessionid      = ""
        self.token          = ""
        self.tokenexpiresat = -1
        self.refreshuntil   = -1
        self.clear_cookie()
        self.save_cookies()

#==============================================================================
# This area defines some routines for unit testing

    #--------------------------------------------------------------------------
    #
    # This routine will return an ElementTree for testing getAuditResults XML
    # (the audit results for one TeraPack).
    #
    def create_audit_results_XML_records(self):

        try:
            inventory = xml.etree.ElementTree.Element("inventory")

            auditResults = xml.etree.ElementTree.SubElement(inventory, "auditResults")

            elementType = xml.etree.ElementTree.SubElement(auditResults, "elementType")
            elementType.text = "storage"

            offset = xml.etree.ElementTree.SubElement(auditResults, "offset")
            offset.text = "1"

            magbarcode = xml.etree.ElementTree.SubElement(auditResults, "barcode")
            #magbarcode.text = "CL0123X" # LTO (10 slots)
            magbarcode.text = "CJ0123X" # TS11xx (9 slots)

            contentsMatch = xml.etree.ElementTree.SubElement(auditResults, "contentsMatch")
            contentsMatch.text = "no"

            expectedContents = xml.etree.ElementTree.SubElement(auditResults, "expectedContents")

            slot = xml.etree.ElementTree.SubElement(expectedContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "1"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            barcode.text = "CLN001LX"

            slot = xml.etree.ElementTree.SubElement(expectedContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "2"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            barcode.text = "CLN002LX"

            slot = xml.etree.ElementTree.SubElement(expectedContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "3"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            barcode.text = "CLN003LX"

            slot = xml.etree.ElementTree.SubElement(expectedContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "4"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            barcode.text = "CLN004LX"

            slot = xml.etree.ElementTree.SubElement(expectedContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "5"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            barcode.text = "CLN005LX"

            #slot = xml.etree.ElementTree.SubElement(expectedContents, "slot")
            #number = xml.etree.ElementTree.SubElement(slot, "number")
            #number.text = "6"
            #barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            #barcode.text = "CLN006LX"

            slot = xml.etree.ElementTree.SubElement(expectedContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "7"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            barcode.text = "CLN007LX"

            slot = xml.etree.ElementTree.SubElement(expectedContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "8"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            barcode.text = "CLN008LX"
            #barcode.text = "CLNXX8LX"

            #slot = xml.etree.ElementTree.SubElement(expectedContents, "slot")
            #number = xml.etree.ElementTree.SubElement(slot, "number")
            #number.text = "9"
            #barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            #barcode.text = "CLN009LX"

            slot = xml.etree.ElementTree.SubElement(expectedContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "10"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            barcode.text = "CLN010LX"

            actualContents = xml.etree.ElementTree.SubElement(auditResults, "actualContents")

            slot = xml.etree.ElementTree.SubElement(actualContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "1"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            #barcode.text = "CLN001LX"
            barcode.text = "CLNBADLX"

            #slot = xml.etree.ElementTree.SubElement(actualContents, "slot")
            #number = xml.etree.ElementTree.SubElement(slot, "number")
            #number.text = "2"
            #barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            #barcode.text = "CLN002LX"

            slot = xml.etree.ElementTree.SubElement(actualContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "3"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            barcode.text = "CLN003LX"

            #slot = xml.etree.ElementTree.SubElement(actualContents, "slot")
            #number = xml.etree.ElementTree.SubElement(slot, "number")
            #number.text = "4"
            #barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            #barcode.text = "CLN004LX"

            slot = xml.etree.ElementTree.SubElement(actualContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "5"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            barcode.text = "CLN005LX"

            #slot = xml.etree.ElementTree.SubElement(actualContents, "slot")
            #number = xml.etree.ElementTree.SubElement(slot, "number")
            #number.text = "6"
            #barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            #barcode.text = "CLN006LX"

            slot = xml.etree.ElementTree.SubElement(actualContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "7"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            barcode.text = "CLN007LX"

            slot = xml.etree.ElementTree.SubElement(actualContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "8"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            barcode.text = "CLN008LX"

            slot = xml.etree.ElementTree.SubElement(actualContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "9"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            barcode.text = "CLN009LX"

            slot = xml.etree.ElementTree.SubElement(actualContents, "slot")
            number = xml.etree.ElementTree.SubElement(slot, "number")
            number.text = "10"
            barcode = xml.etree.ElementTree.SubElement(slot, "barcode")
            barcode.text = "CLN010LX"

        except Exception as e:
            raise(Exception("create_audit_results_XML_records Error creating XML"))

        return(inventory)

#==============================================================================
def main():

    # Define defaults here
    default_configfile = "/etc/slapi.conf"

    cmdparser     = argparse.ArgumentParser(description='Spectra Logic TFinity API Tool.')
    cmdsubparsers = cmdparser.add_subparsers(title="commands", dest="command")

    cmdparser.add_argument('--version', '-V', action='version', version='%(prog)s @VERSION@')

    cmdparser.add_argument('--verbose', '-v', dest='verbose', action='store_true',
                           help='Increase the verbosity for the output.')

    cmdparser.add_argument('--longlist', '-l', dest='longlist', action='store_true',
                           help='Format the output as a long listing; one     \
                           attribute per line. Easier for the human eye; but  \
                           difficult to parse.')

    cmdparser.add_argument('--insecure', '-i', dest='insecure', action='store_true',
                           help='Communicate with library over http:// instead of https://')

    cmdparser.add_argument('--config', '-c', dest='configfile', nargs='?',
                           type=str, required=False, default=default_configfile,
                           help='Configuration file for Spectra Logic API.')

    cmdparser.add_argument('--server', '-s', dest='server',
                           required=True,
                           help='Hostname/IP Address of Spectra Logic Library.')

    cmdparser.add_argument('--port', '-P', dest='port',
                           type=int, required=False,
                           help='Port to connect to for bluescale.')

    cmdparser.add_argument('--user', '-u', dest='user',
                           help='User name for Spectra Logic Library Login.')

    pwaction = cmdparser.add_mutually_exclusive_group(required = False)
    pwaction.add_argument('--insecure-passwd', '-I', dest='passwd',
                          help='Password for Spectra Logic Library Login. ' +
                               'Do not use this option if you care about security. ' +
                               'Specify the password in the config file instead.')

    pwaction.add_argument('--passwd', '-p', dest='passwd_prompt', action='store_true',
                          help='Prompt user for password to Spectra Logic Library.')

    frus_parser = cmdsubparsers.add_parser('frus',
        help='Retrieve a list of hardware field replaceable units currently in the library.')

    inventory_parser = cmdsubparsers.add_parser('inventory',
        help='Retrieve inventory from the library.')

    librarystatus_parser = cmdsubparsers.add_parser('librarystatus',
        help='Retrieve library status information.')

    login_parser = cmdsubparsers.add_parser('login',
        help='Login and get tokens from the library.')

    spec_parser = cmdsubparsers.add_parser('spec',
        help='Get the newest REST API spec.')

    args = cmdparser.parse_args()
    if args.passwd_prompt:
        args.passwd = getpass.getpass()

    if args.configfile is not None:

        if args.configfile == default_configfile and os.access(args.configfile, os.R_OK) is False:
            pass
        elif os.access(args.configfile, os.R_OK) is False:
            print("Cannot access configfile " + args.configfile, file=sys.stderr)
            sys.exit(1)

        cfgparser = configparser.ConfigParser(allow_no_value=True)
        cfgparser.read(args.configfile)

        try:
            config = cfgparser[args.server]
        except Exception as e:
            config = cfgparser["DEFAULT"]

        try:
            if args.user is None:
                if config.get("username"):
                    args.user   = config["username"]
            if args.passwd is None:
                if config.get("password"):
                    args.passwd = config["password"]
                if "password" in config.keys():
                    if config["password"] is None or config["password"] == "":
                        args.passwd = ""
            if args.insecure is None or args.insecure == False:
                if config.get("insecure"):
                    args.insecure = config.getboolean("insecure")
            if args.verbose is None or args.verbose == False:
                if config.get("verbose"):
                    args.verbose = config.getboolean("verbose")
            if args.port is None:
                if config.get("port"):
                    args.port    = config.getint("port")

        except Exception as e:
            print(str(e))
            cmdparser.print_help()
            sys.exit(1)

    try:
        if args.server is None or args.server == "":
            raise(Exception("Error: SERVER not specified"))
        if args.user is None or args.user == "":
            raise(Exception("Error: USER not specified"))
        if args.passwd is None:
            raise(Exception("Error: PASSWD not specified"))
    except Exception as e:
        print(str(e))
        sys.exit(1)

    slapi = SpectraLogicAPI(args)

    try:
        if args.command is None:
            cmdparser.print_help()
            sys.exit(1)
        elif args.command == "frus":
            slapi.frus()
        elif args.command == "inventory":
            slapi.inventory()
        elif args.command == "librarystatus":
            slapi.librarystatus()
        elif args.command == "login":
            slapi.login()
        elif args.command == "spec":
            slapi.spec()
        else:
            cmdparser.print_help()
            sys.exit(1)
    except Exception as e:
        fullcommand = args.command
        if hasattr(args, "subcommand") and args.subcommand is not None:
            fullcommand = args.command + " " + args.subcommand
        print("Command '" + fullcommand + "': " + str(e), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
