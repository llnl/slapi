#!/usr/bin/env python3.11
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

import sys
import os
# Use the local lumosapi_client if it exists
if os.path.isdir("lumosapi_client"):
    sys.path.append("lumosapi_client")

import argparse
import getpass
import functools
import stat
import time
import pathlib
import configparser
import logging
import urllib.request
import urllib.error
import platform
import json
import datetime
import re
import pandas
from pprint import pprint
import importlib

import lumosapi_client
from lumosapi_client.models.fru_list import FRUList
from lumosapi_client.models.fru_types import FRUTypes
from lumosapi_client.rest import ApiException

class SpectraLogicLoginError(Exception):

    LoginErrorRaised = False

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class SpectraLogicAPI:

    #--------------------------------------------------------------------------
    #
    def __init__(self, args):
        self.first_try         = True
        self.server            = args.server
        self.port              = args.port
        self.user              = args.user
        self.passwd            = args.passwd
        self.json              = args.json
        self.debug             = args.debug
        self.insecure          = args.insecure
        self.longlist          = args.longlist
        self.loggedin          = False
        self.token             = ""
        self.tokenexpiresat    = -1
        self.refreshuntil      = -1
        self.cookiefile        = self.slapi_directory() + "/cookies_lumos.txt"
        if args.insecure == False:
            httpstr = "https://"
        else:
            httpstr = "http://"
        self.baseurl = httpstr + args.server + "/api"
        if args.port is not None:
            self.baseurl = httpstr + args.server + ":" + str(args.port) + "/api"

        self.load_cookie()

        if self.token == "":
            self.configuration = lumosapi_client.Configuration(host=f"{self.baseurl}")
        else:
            self.configuration = lumosapi_client.Configuration(host=f"{self.baseurl}",
                                                               access_token=self.token)

        self.configuration.verify_ssl = False
        self.configuration.client_side_validation = False
        self.configuration.debug = args.debug

        # Initialize pandas default settings
        pandas.options.display.max_columns = None
        pandas.options.display.max_colwidth = None
        pandas.options.display.max_rows = None
        pandas.set_option('expand_frame_repr', False)

    #--------------------------------------------------------------------------
    #
    def token_to_json(self):
        return {'server': self.server,
                'token': self.token,
                'token_expires_at': self.tokenexpiresat,
                'refresh_until': self.refreshuntil}

    #--------------------------------------------------------------------------
    #
    def __str__(self):
        return(f"Server:        {self.server}\n"
               f"Port:          {self.port}\n"
               f"Username:      {self.user}\n"
               f"Password:      ****\n"
               f"Json:          {self.json}\n"
               f"Debug:         {self.debug}\n"
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
            if now >= self.tokenexpiresat:
                return(True)
            else:
                return(False)

        except Exception as e:
            return(True)

    #--------------------------------------------------------------------------
    #
    def clear_cookie(self):
        try:
            os.umask(0o077)
            found = False

            # Save all cookies in a list
            json_list = []
            if os.path.exists(self.cookiefile):
                with open(self.cookiefile, 'r') as cookiefile:
                    for line in cookiefile:
                        # Do not add the cookie in question to our list
                        if json_obj['server'] != self.server:
                            json_obj = json.loads(line)
                            json_list.append(json_obj)

            # Save all cookies to file
            with open(self.cookiefile, 'w') as cookiefile:
                for json_obj in json_list:
                    json.dump(json_obj, cookiefile)

        except Exception as e:
            self.loggedin       = False
            self.token          = ""
            self.tokenexpiresat = -1
            self.refreshuntil   = -1

    #--------------------------------------------------------------------------
    #
    def load_cookie(self):

        try:
            with open(self.cookiefile, 'r') as cookiefile:
                for line in cookiefile:
                    json_obj = json.loads(line)
                    if json_obj['server'] == self.server:
                        # Found it we will load the cookie
                        self.token = json_obj['token']
                        self.tokenexpiresat = json_obj['token_expires_at']
                        self.refreshuntil = json_obj['refresh_until']
                        break

        except Exception as e:
            self.save_cookies()
            self.loggedin       = False
            self.token          = ""
            self.tokenexpiresat = -1
            self.refreshuntil   = -1

    #--------------------------------------------------------------------------
    #
    def save_cookies(self):

        try:

            os.umask(0o077)
            found = False

            # Save all cookies in a list
            json_list = []
            if os.path.exists(self.cookiefile):
                with open(self.cookiefile, 'r') as cookiefile:
                    for line in cookiefile:
                        json_obj = json.loads(line)
                        json_list.append(json_obj)

            # Overwrite cookie for server in question
            for json_obj in json_list:
                if json_obj['server'] == self.server:
                    json_obj['token'] = self.token
                    json_obj['token_expires_at'] = self.tokenexpiresat
                    json_obj['refresh_until'] = self.refreshuntil
                    found = True

            if not found:
                json_obj = self.token_to_json()
                json_list.append(json_obj)

            # Save all cookies to file
            with open(self.cookiefile, 'w') as cookiefile:
                for json_obj in json_list:
                    json.dump(json_obj, cookiefile)

        except Exception as e:
            print(f"{e}")
            os.umask(0o077)
            self.loggedin       = False
            self.token          = ""
            self.tokenexpiresat = -1
            self.refreshuntil   = -1

    #--------------------------------------------------------------------------
    #
    # This routine pretty prints the JSON document
    #
    def print_json_document(self, jsonstr):

        jsonobj = json.loads(jsonstr)
        json_pretty_str = json.dumps(jsonobj, indent=2)
        json_lines = json_pretty_str.splitlines()
        for line in json_lines:
            line = line.rstrip()
            if line != "":
                print(line)

    #--------------------------------------------------------------------------
    #
    #
    def slapi_print(self, dataframe):

        if self.json:
            if dataframe is not None:
                self.print_json_document(dataframe.to_json(orient='records'))
        else:
            if dataframe is None:
                print()
                return
            print(dataframe.to_markdown(index=False, tablefmt='simple'))

    #==========================================================================
    # DEFINE COMMAND FUNCTIONS
    #==========================================================================

    def drivesummary(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get the inventory from the library
            api_response = api_instance.get_drives_summary()
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc), record_path='value')
            self.slapi_print(dataframe)

    def frus(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get Metadata for FRUs in the library
            api_response = api_instance.get_frus()

            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc), record_path='value')
            dataframe.pop('actions.count')
            dataframe.pop('actions.value')

            fru_type = None
            dataframe_fru = None
            for index, fru in dataframe.iterrows():
                api_response = api_instance.get_fru_status(fru['name'])
                json_doc_fru = api_response.to_json()
                tmp_dataframe_fru = pandas.json_normalize(json.loads(json_doc_fru))

                if fru['type'] != fru_type:
                    if fru_type != None:
                        self.slapi_print(dataframe_fru)
                        self.slapi_print(None)
                    dataframe_fru = tmp_dataframe_fru
                    printheader = True
                    fru_type = fru['type']
                else:
                    dataframe_fru.loc[len(dataframe_fru)] = json.loads(json_doc_fru)

            # Print the final one
            self.slapi_print(dataframe_fru)

    def inventory(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get the inventory from the library
            api_response = api_instance.get_inventory()
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc), record_path='value')
            dataframe = dataframe.sort_values(by=['partition', 'address'])
            self.slapi_print(dataframe)

    def librarystatus(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Retrieve Current Library Status
            api_response = api_instance.get_library_status()
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc))
            dataframe = dataframe.explode('doors')
            dataframe_doors = dataframe.pop('doors')
            dataframe_doors = dataframe_doors['doors'].apply(pandas.Series)
            self.slapi_print(dataframe)
            self.slapi_print(dataframe_doors)

    #--------------------------------------------------------------------------
    #
    # Connects to the library using the specified username and password. See
    # "Configuring Library Users" in your library User Guide for information
    # about configuring users and passwords, as well as information about what
    # sort of actions each user type can perform.
    #
    def login(self):

        try:
            # Enter a context with an instance of the API client
            with lumosapi_client.ApiClient(self.configuration) as api_client:
                # Create an instance of the API class
                api_instance = lumosapi_client.TFinityApi(api_client)
                login_request = lumosapi_client.LoginRequest(domain = "NATIVE",
                                                             username = self.user,
                                                             password = self.passwd)
                # Request Authorization Token (JWT)
                api_response = api_instance.login(login_request)

                if api_response.password_has_expired:
                    self.loggedin       = False
                    self.token          = ""
                    self.tokenexpiresat = -1
                    self.refreshuntil   = -1
                    self.clear_cookie()
                    self.save_cookies()

                # The login succeeded
                self.loggedin = True
                self.refreshuntil = api_response.refresh_until
                self.token = api_response.token
                self.tokenexpiresat = api_response.token_expires_at
                self.configuration = lumosapi_client.Configuration(host=f"{self.baseurl}",
                                                                   access_token=self.token)
                self.configuration.verify_ssl = False
                self.configuration.client_side_validation = False

                self.save_cookies()
                
        except lumosapi_client.exceptions.UnauthorizedException as e:
            if self.debug:
                print("Login Failed...", file=sys.stderr)
            self.loggedin       = False
            self.token          = ""
            self.tokenexpiresat = -1
            self.refreshuntil   = -1
            self.clear_cookie()
            self.save_cookies()
            if self.first_try:
                self.first_try = False
                self.login()
        except Exception as e:
            if self.debug:
                print(f"Exception when calling TFinityApi->login ({type(e).__name__} {e})", file=sys.stderr)
            self.loggedin       = False
            self.token          = ""
            self.tokenexpiresat = -1
            self.refreshuntil   = -1
            self.clear_cookie()
            self.save_cookies()
            if self.first_try:
                self.first_try = False
                self.login()

    def robotservice(self, robot, action):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            if robot == "1":
                robot = "Robot:1"
            elif robot == "2":
                robot = "Robot:2"
            else:
                raise(Exception("Error: Invalid robotservice robot number"))

            if action.lower() == "beginservice":
                action = "BEGIN_SERVICE"
            elif action.lower() == "endservice":
                action = "END_SERVICE"
            else:
                raise(Exception("Error: Invalid robotservice robot action"))

            # Get the inventory from the library
            api_response = api_instance.start_fru_action(robot, action)
            task_id = api_response.task_id

            i = 1
            while (1):
                api_response = api_instance.get_task(task_id)
                state = api_response.state
                log = api_response.task_log
                if state == lumosapi_client.TaskStates.SUCCEEDED:
                    print(f"Robot move succeeded.")
                    break
                elif i >= 100:
                    raise(Exception("Error: Timed out waiting for robot move to complete"))
                else:
                    print(f"{state} {api_response}")
                i = i+1
                time.sleep(5)

    def spec(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get API spec from the library
            api_response = api_instance.get_api_documentation()
            pprint(api_response)

    def packagelist(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get the active package from the library
            api_response_active = api_instance.get_active_package()
            json_doc_active = api_response_active.to_json()

            # Get packages from the library
            api_response = api_instance.get_packages()
            json_doc = api_response.to_json()

            dataframe_active = pandas.json_normalize(json.loads(json_doc_active), record_path='firmware', meta=['name', 'version', 'created'], record_prefix='firmware.')
            dataframe_packages = pandas.json_normalize(json.loads(json_doc), record_path='value')

            dataframe = dataframe_packages.explode('firmware')
            dataframe_firmware = dataframe['firmware'].apply(pandas.Series)
            # We need to add a prefix for the firmware to ensure that the
            # keys in the dictionary are unique
            dataframe_firmware = dataframe_firmware.add_prefix('firmware.')
            dataframe = pandas.concat([dataframe.drop(['firmware'], axis=1), dataframe_firmware], axis=1)
            self.slapi_print(dataframe)
            self.slapi_print(None)

            # We need to add a prefix for the firmware to ensure that the
            # keys in the dictionary are unique
            firmware_name_column = dataframe_active.pop('firmware.name')
            firmware_version_column = dataframe_active.pop('firmware.version')
            dataframe_active['firmware.name'] = firmware_name_column
            dataframe_active['firmware.version'] = firmware_version_column
            dataframe_active = dataframe_active.add_prefix('active.')
            self.slapi_print(dataframe_active)

    def packagedelete(self, package_file):

        try:
            # Enter a context with an instance of the API client
            with lumosapi_client.ApiClient(self.configuration) as api_client:
                # Create an instance of the API class
                api_instance = lumosapi_client.TFinityApi(api_client)

                # Remove package from the library
                api_response = api_instance.delete_package(package_file)
                # If we got here assume the package was deleted successfully
                print(f"Package {package_file} successfully deleted from library.")

        except lumosapi_client.exceptions.NotFoundException as e:
            print(f"Package {package_file} is not stored on the library.")
            sys.exit(1)

    def packageupdate(self, package_file):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)
            package_update_request = lumosapi_client.PackageUpdateRequest(name=package_file)

            # Upload package file to the library
            api_response = api_instance.start_library_update(package_update_request)
            pprint(api_response)

    def packageupdatestatus(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Upload package file to the library
            api_response = api_instance.get_package_update_state()
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc))
            print(dataframe.to_string(index=False))
            print("")
            pprint(api_response)

    def packageupload(self, package_file, pubkey_file):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Upload package file to the library
            api_response = api_instance.upload_package(package_file=package_file, pubkey_file=pubkey_file)
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc), record_path='firmware', meta=['name', 'version', 'created'], record_prefix='firmware.')
            firmware_name_column = dataframe.pop('firmware.name')
            firmware_version_column = dataframe.pop('firmware.version')
            dataframe['firmware.name'] = firmware_name_column
            dataframe['firmware.version'] = firmware_version_column
            self.slapi_print(dataframe)

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

    cmdparser.add_argument('--json', '-j', dest='json', action='store_true',
                           help='Print out everything in JSON.')

    cmdparser.add_argument('--debug', '-d', dest='debug', action='store_true',
                           help='Add debugging output.')

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

    frus_parser = cmdsubparsers.add_parser('drivesummary',
        help='Get a summary of drives.')

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

    package_parser = cmdsubparsers.add_parser('package',
        help='package command help.')
    package_subparser = package_parser.add_subparsers(title="subcommands", dest="subcommand")

    package_delete_parser = package_subparser.add_parser('delete',
        help='Delete a software package from the library.')
    package_delete_parser.add_argument('package_file', action='store',
        help='Software package file to delete.')

    package_list_parser = package_subparser.add_parser('list',
        help='List software packages sotred on the library.')

    package_update_parser = package_subparser.add_parser('update',
        help='Update library to new software package.')
    package_update_parser.add_argument('package_file', action='store',
        help='Software package file to update library to.')

    package_updatestatus_parser = package_subparser.add_parser('updatestatus',
        help='Get software update status from the library.')

    package_upload_parser = package_subparser.add_parser('upload',
        help='Upload a new software package to the library.')
    package_upload_parser.add_argument('package_file', action='store',
        help='Path to software package file to upload.')
    package_upload_parser.add_argument('pubkey_file', action='store',
        help='Path to software package verification file to upload.')

    robotservice_parser = cmdsubparsers.add_parser('robotservice',
        help='Send robot to/from service bay.')
    robotservice_subparser = robotservice_parser.add_subparsers(title="subcommands", dest="subcommand")
    robotservice_beginservice_parser = robotservice_subparser.add_parser('beginservice', help='Move robot to the service bay')
    robotservice_beginservice_parser.add_argument('robot',
        action='store',
        type=str.lower,
        default=None,
        choices=['1', '2'],
        help='Left robot (1) or right robot (2) when facing the front of the library.')
    robotservice_endservice_parser = robotservice_subparser.add_parser('endservice', help='Move robot out of service bay')
    robotservice_endservice_parser.add_argument('robot',
        action='store',
        type=str.lower,
        default=None,
        choices=['1', '2'],
        help='Left robot (1) or right robot (2) when facing the front of the library.')

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
            if args.json is None or args.json == False:
                if config.get("json"):
                    args.json = config.getboolean("json")
            if args.debug is None or args.debug == False:
                if config.get("debug"):
                    args.debug = config.getboolean("debug")
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

    while slapi.first_try == True:
        try:
            if args.command is None:
                cmdparser.print_help()
                sys.exit(1)
            elif args.command == "drivesummary":
                slapi.drivesummary()
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
            elif args.command == "package":
                if args.subcommand is None or args.subcommand == "list":
                    slapi.packagelist()
                elif args.subcommand == "delete":
                    slapi.packagedelete(args.package_file)
                elif args.subcommand == "update":
                    slapi.packageupdate(args.package_file)
                elif args.subcommand == "updatestatus":
                    slapi.packageupdatestatus()
                elif args.subcommand == "upload":
                    slapi.packageupload(args.package_file, args.pubkey_file)
                else:
                    raise(Exception("package: Unknown option " + args.subcommand))
            elif args.command == "robotservice":
                slapi.robotservice(robot=args.robot, action=args.subcommand)
            else:
                cmdparser.print_help()
                sys.exit(1)

        except lumosapi_client.exceptions.UnauthorizedException as e:
            if slapi.debug:
                print("Unauthorized...Logging in again...", file=sys.stderr)
            slapi.login()
        except lumosapi_client.exceptions.ConflictException as e:
            json_doc = json.loads(e.body)
            print(f"Error ({json_doc['error']['code']}): {json_doc['error']['message']}")
            sys.exit(1)
        except lumosapi_client.exceptions.UnprocessableEntityException as e:
            json_doc = json.loads(e.body)
            print(f"Error ({json_doc['error']['code']}): {json_doc['error']['message']}")
            sys.exit(1)
        except Exception as e:
            fullcommand = args.command
            if hasattr(args, "subcommand") and args.subcommand is not None:
                fullcommand = args.command + " " + args.subcommand
            print("Command '" + fullcommand + "': " + str(e), file=sys.stderr)
            print(type(e))
            sys.exit(1)
        finally:
            slapi.first_try = False

if __name__ == "__main__":
    main()
