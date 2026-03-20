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
import argparse
import getpass
import functools
import stat
import time
import pathlib
import configparser
import logging
import urllib3
import platform
import json
import datetime
import pytz
import re
import pandas
import importlib
from pprint import pprint

# Use the local lumosapi_client if it exists
slapipath = os.path.abspath(__file__)
slapidir  = os.path.dirname(slapipath)
lumospath = f"{slapidir}/lumosapi_client"
if os.path.isdir(f"{lumospath}"):
    sys.path.insert(0, f"{lumospath}")

import lumosapi_client
from lumosapi_client.models.fru_list import FRUList
from lumosapi_client.models.fru_types import FRUTypes
from lumosapi_client.rest import ApiException

def drivelocation_to_string(drivelocation):
    if isinstance(drivelocation, dict):
        mystr = f"{drivelocation['frame']}:{drivelocation['dba']}:{drivelocation['chamber']}"
        return(f"{mystr}")
    return str(drivelocation)

def driveport_to_string(driveport):
    if isinstance(driveport, dict):
        mystr = f"{driveport['addressMode']}"
        return(f"{mystr}")
    return str(driveport)

class SpectraLogicLoginError(Exception):

    LoginErrorRaised = False

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class SpectraLogicAPI:

    #--------------------------------------------------------------------------
    #
    def __init__(self, args):
        self.num_tries         = 0
        self.server            = args.server
        self.port              = args.port
        self.user              = args.user
        self.passwd            = args.passwd
        self.json              = args.json
        self.debug             = args.debug
        self.verbose           = args.verbose
        self.insecure          = args.insecure
        self.longlist          = args.longlist
        self.loggedin          = False
        self.token             = ""
        self.tokenexpiresat    = -1
        self.refreshuntil      = -1
        self.wait              = args.wait
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

        # Set the number of retries
        self.configuration.retries = 1

        # Initialize the datetime format for commands
        self.configuration.datetime_format = "%Y-%m-%dT%H:%M:%SZ"

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
            raise(Exception(f"{home} does not exist."))
        if os.path.isdir(home) == False:
            raise(Exception(f"{home} is not a directory."))

        slapidir = home + "/.slapi"
        if os.path.exists(slapidir):
            if os.path.isdir(slapidir):
                return(slapidir)
            else:
                raise(Exception(f"{slapidir} is not a directory."))
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

            # Only add in the new token if it is set
            if not found and self.token:
                json_obj = self.token_to_json()
                json_list.append(json_obj)

            # Save all cookies to file
            with open(self.cookiefile, 'w') as cookiefile:
                for json_obj in json_list:
                    json.dump(json_obj, cookiefile)
                    print("", file=cookiefile)

        except Exception as e:
            print(f"{e}", file=sys.stderr)
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
                print(line, flush=True)

    #--------------------------------------------------------------------------
    #
    #
    def slapi_print(self, dataframe):

        if self.json:
            if dataframe is not None:
                self.print_json_document(dataframe.to_json(orient='records'))
        else:
            if dataframe is None:
                print(flush=True)
                return
            print(dataframe.to_markdown(index=False, tablefmt='simple'), flush=True)

    #==========================================================================
    # DEFINE SHARED COMMAND FUNCTIONS
    #==========================================================================

    def get_partition_dataframe(self, partition=None):

        dataframe_partition = None

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # If the partition is not specifified then get a list of all the
            # partitions in the library
            if partition is None:
                api_response = api_instance.get_partitions()

                for partition_data in api_response:
                    json_doc = partition_data.to_json()
                    dataframe = pandas.json_normalize(json.loads(json_doc))
                    dataframe_partition = pandas.concat([dataframe_partition, dataframe])
            else:
                api_response = api_instance.get_partition(partition=partition)
                json_doc = api_response.to_json()
                dataframe_partition = pandas.json_normalize(json.loads(json_doc))
            dataframe_partition = dataframe_partition.sort_values(by=['id'])
            return(dataframe_partition)

    def get_inventoryfull_dataframe(self, partition=None):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get the inventory from the library
            api_response = api_instance.get_inventory(partition=partition)
            json_doc = api_response.to_json()
            dataframe_inventory = pandas.json_normalize(json.loads(json_doc), record_path='value')
            dataframe_inventory = dataframe_inventory.sort_values(by=['partition', 'address'])

            # Looks like sourceAddress is not always in the output.
            # When carts begin to move these begin to get filled in, so sometimes
            # we have to manually add it in.
            if "sourceAddress" not in dataframe_inventory.columns:
                address_column_index = dataframe_inventory.columns.get_loc("address")
                dataframe_inventory.insert(address_column_index+1, "sourceAddress", pandas.Series())
            else:
                source_address_column = dataframe_inventory.pop("sourceAddress")
                address_column_index = dataframe_inventory.columns.get_loc("address")
                dataframe_inventory.insert(address_column_index+1, "sourceAddress", source_address_column)

            # Retrieve TeraPack Magazine Information
            api_response = api_instance.get_magazines(partition=partition)
            json_doc = api_response.to_json()
            dataframe_magazines = pandas.json_normalize(json.loads(json_doc), record_path='value')
            dataframe_magazines = dataframe_magazines.explode('slots')
            dataframe_slots = dataframe_magazines['slots'].apply(pandas.Series)
            dataframe_slots = dataframe_slots.add_prefix('slot.')
            dataframe_magazines = pandas.concat([dataframe_magazines.drop(['slots'], axis=1), dataframe_slots], axis=1)
            dataframe_magazines = dataframe_magazines.sort_values(by=['slot.partition', 'slot.address', 'barcode'])
            dataframe_magazines.pop('state')
            dataframe_magazines.pop('slot.containerState')

            dataframe = pandas.merge(dataframe_inventory, dataframe_magazines, left_on=['partition', 'address'], right_on=['slot.partition', 'slot.address'], how='outer')
            dataframe.pop('slot.address')
            dataframe.pop('slot.containerType')
            dataframe.pop('slot.mediaType')
            dataframe.pop('slot.partition')
            dataframe.pop('slot.mediaBarcode')
            dataframe = dataframe.rename(columns={'barcode': 'magazineBarcode'})
            return(dataframe)

    #==========================================================================
    # DEFINE COMMAND FUNCTIONS
    #==========================================================================

    def dlmlist(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get DLM Records from the library
            api_response = api_instance.get_dlm()
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc), record_path='value')
            #dataframe = dataframe.sort_values(by=['currentPartition', 'barcode', 'tapeSerial'])

            #dataframe.pop('MAMReadOnLoad')
            #dataframe.pop('isTapeRead')
            #dataframe.pop('lastLoadedPartition')
            #dataframe.pop('manufacturerID')
            #dataframe.pop('firstWriteLibrary')
            #dataframe.pop('firstWritePartition')
            #dataframe.pop('export')
            #dataframe.pop('import')
            #dataframe = dataframe.loc[:,~dataframe.columns.str.startswith('readWrite.')]
            #dataframe = dataframe.loc[:,~dataframe.columns.str.startswith('encryption.')]

            self.slapi_print(dataframe)

    def drivelist(self, partition=None):

        dataframe_partition = self.get_partition_dataframe(partition=partition)
        dataframe_drives = dataframe_partition.pop('drives')
        dataframe_drives = dataframe_drives.explode('drives').to_frame()
        dataframe_drives = dataframe_drives['drives'].apply(pandas.Series)

        # convert the physicalDrive into multiple columns
        dataframe_physicaldrives = pandas.json_normalize(dataframe_drives['physicalDrive'])
        dataframe_drives = dataframe_drives.drop('physicalDrive', axis=1).join(dataframe_physicaldrives)

        dataframe_drives['location'] = dataframe_drives['location'].apply(drivelocation_to_string)
        dataframe_drives['physicalLocation'] = dataframe_drives['physicalLocation'].apply(drivelocation_to_string)
        dataframe_drives['portConfiguration'] = dataframe_drives['portConfiguration'].apply(driveport_to_string)

        dataframe_drives.pop('drivePath')
        dataframe_drives.pop('location')
        dataframe_drives.pop('exporting')
        dataframe_drives.pop('patchLevel')
        self.slapi_print(dataframe_drives)

    def drivesummary(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get drive summary from the library
            api_response = api_instance.get_drives_summary()
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc), record_path='value')
            self.slapi_print(dataframe)

    def environmentlist(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get the library environmental summary
            api_response = api_instance.get_environment_summary()
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
                if self.debug:
                    print(f"Getting FRU status for: {fru['name']}...", file=sys.stderr)

                # Below we explicitly set the _request_timeout.
                # We have seen problematic drives take 5-10 minutes to respond to this API
                # call, so make sure to limit how long we wait here.
                # If we fail we mark the state as UNKNOWN.
                try:
                    api_response = api_instance.get_fru_status(fru['name'], _request_timeout=10.0)
                    json_doc_fru = api_response.to_json()
                except urllib3.exceptions.MaxRetryError as e:
                    json_string = { "name": fru['name'],
                                    "status": "UNKNOWN",
                                    "type": "DRIVE"
                    }
                    json_doc_fru = json.dumps(json_string)

                tmp_dataframe_fru = pandas.json_normalize(json.loads(json_doc_fru))

                if fru['type'] != fru_type:
                    if fru_type != None:
                        self.slapi_print(dataframe_fru)
                        self.slapi_print(None)
                    dataframe_fru = tmp_dataframe_fru
                    printheader = True
                    fru_type = fru['type']
                else:
                    dataframe_fru = pandas.concat([dataframe_fru, tmp_dataframe_fru])

            # Print the final one
            self.slapi_print(dataframe_fru)

    def humiditymetrics(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get the humidity metrics from the library
            # For now we only try to get the most recent reading
            # Hard code to 10 min interval 10 mins ago
            start_time = (datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0) - datetime.timedelta(seconds=600)).strftime("%Y-%m-%dT%H:%M:%SZ")
            api_response = api_instance.get_humidity_metrics(start_time=start_time, interval="10m")
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc))

            for column_name in dataframe.columns:
               tmp_dataframe = dataframe.pop(column_name)
               tmp_dataframe = tmp_dataframe.explode(column_name).to_frame().dropna()
               if not tmp_dataframe.empty:
                   tmp_dataframe = tmp_dataframe[column_name].apply(pandas.Series)
                   tmp_dataframe = tmp_dataframe.add_prefix(f"{column_name}.")
                   self.slapi_print(tmp_dataframe)
                   self.slapi_print(None)

    def inventory(self, partition=None):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get the inventory from the library
            api_response = api_instance.get_inventory(partition=partition)
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc), record_path='value')
            dataframe = dataframe.sort_values(by=['partition', 'address'])

            # Looks like sourceAddress is not always in the output.
            # When carts begin to move these begin to get filled in, so sometimes
            # we have to manually add it in.
            if "sourceAddress" not in dataframe.columns:
                address_column_index = dataframe.columns.get_loc("address")
                dataframe.insert(address_column_index+1, "sourceAddress", pandas.Series())
            else:
                source_address_column = dataframe.pop("sourceAddress")
                address_column_index = dataframe.columns.get_loc("address")
                dataframe.insert(address_column_index+1, "sourceAddress", source_address_column)

            self.slapi_print(dataframe)

    def inventoryfull(self, partition=None):

        dataframe = self.get_inventoryfull_dataframe(partition=partition)
        self.slapi_print(dataframe)

    def librarystatus(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Retrieve Library Info
            api_response = api_instance.get_library_info()
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc))
            dataframe.pop('timeSource')
            dataframe.pop('frontPanelTimezone')
            dataframe.pop('ec')
            dataframe.pop('topLevelAssemblyEC')
            dataframe.pop('topLevelAssemblySerialNumber')
            self.slapi_print(dataframe)
            self.slapi_print(None)

            # Retrieve Current Library Status
            api_response = api_instance.get_library_status()
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc))
            dataframe_doors = dataframe.pop('doors')
            dataframe_doors = dataframe_doors.explode('doors').to_frame()
            dataframe_doors = dataframe_doors['doors'].apply(pandas.Series)
            self.slapi_print(dataframe)
            self.slapi_print(None)
            self.slapi_print(dataframe_doors)

    def logdownload(self, logname=None, logtype=None, logdate=None):
        write_size = 1024

        if logname is None:
            raise(Exception(f"Error: Invalid filename specfied."))

        if logtype is None:
            raise(Exception(f"Error: Invalid log type specified."))

        end_date = datetime.datetime.now() - datetime.timedelta(days=1)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=0)
        if logdate is not None:
            end_date = datetime.datetime.strptime(logdate, "%Y-%m-%dT%H:%M:%S")
            end_date = end_date.replace(microsecond=0)
        start_date = end_date - datetime.timedelta(days=1)

        # Assume the time passed in uses local timezone
        start_date = start_date.astimezone()
        end_date = end_date.astimezone()

        # Convert the time to UTC
        start_date_utc = start_date.astimezone(pytz.utc)
        end_date_utc = end_date.astimezone(pytz.utc)

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get the log from the library
            api_response = api_instance.download_logs_synchronous(log_type=[logtype], save_to_usbs=False, start_time=start_date_utc, end_time=end_date_utc)

            with open(logname, 'wb') as f:
                for i in range(0, len(api_response), write_size):
                    buf = api_response[i : i + write_size]
                    f.write(buf)

    def logtypes(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Retrieve Log Types
            api_response = api_instance.get_log_type_list()

            for key in api_response:
                value = api_response[key]
                dataframe = pandas.DataFrame({key: value})
                self.slapi_print(dataframe)
                self.slapi_print(None)

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

                # Save original configuration
                old_configuration = self.configuration
                self.configuration = lumosapi_client.Configuration(host=f"{self.baseurl}",
                                                                   access_token=self.token)

                # Restore some saved settings
                self.configuration.verify_ssl = old_configuration.verify_ssl
                self.configuration.client_side_validation = old_configuration.client_side_validation
                self.configuration.debug = old_configuration.debug
                self.configuration.datetime_format = old_configuration.datetime_format

                self.save_cookies()

        except lumosapi_client.exceptions.UnauthorizedException as e:
            self.loggedin       = False
            self.token          = ""
            self.tokenexpiresat = -1
            self.refreshuntil   = -1
            self.clear_cookie()
            self.save_cookies()

            if self.verbose or self.num_tries >= 1:
                print(f"Login to {self.server} Failed.", file=sys.stderr)

            if self.num_tries < 1:
                self.num_tries = self.num_tries + 1
                self.login()
            else:
                sys.exit(1)
        except Exception as e:
            if self.verbose:
                print(f"Exception when calling TFinityApi->login ({type(e).__name__} {e})", file=sys.stderr)
            self.loggedin       = False
            self.token          = ""
            self.tokenexpiresat = -1
            self.refreshuntil   = -1
            self.clear_cookie()
            self.save_cookies()
            if self.num_tries < 1:
                self.num_tries = self.num_tries + 1
                self.login()

    def magazines(self, partition=None):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Retrieve TeraPack Magazine Information
            api_response = api_instance.get_magazines(partition=partition)
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc), record_path='value')
            dataframe = dataframe.explode('slots')
            dataframe_slots = dataframe['slots'].apply(pandas.Series)
            dataframe_slots = dataframe_slots.add_prefix('slot.')
            dataframe = pandas.concat([dataframe.drop(['slots'], axis=1), dataframe_slots], axis=1)
            dataframe = dataframe.sort_values(by=['slot.partition', 'slot.address', 'barcode'])
            ignore_column = dataframe.pop('state')
            ignore_column = dataframe.pop('slot.containerState')
            dataframe = dataframe.rename(columns={'barcode': 'magazineBarcode'})
            self.slapi_print(dataframe)

    def messages(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get messages from the library
            api_response = api_instance.get_messages()
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc), record_path='value')
            dataframe.pop('read')
            dataframe.pop('uid')
            dataframe.pop('id')
            self.slapi_print(dataframe)

    def mlmlist(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get MLM Records from the library
            api_response = api_instance.get_mlm()
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc), record_path='value')
            dataframe = dataframe.sort_values(by=['currentPartition', 'barcode', 'tapeSerial'])

            dataframe.pop('MAMReadOnLoad')
            dataframe.pop('isTapeRead')
            dataframe.pop('lastLoadedPartition')
            dataframe.pop('manufacturerID')
            dataframe.pop('firstWriteLibrary')
            dataframe.pop('firstWritePartition')
            dataframe.pop('export')
            dataframe.pop('import')
            dataframe = dataframe.loc[:,~dataframe.columns.str.startswith('readWrite.')]
            dataframe = dataframe.loc[:,~dataframe.columns.str.startswith('encryption.')]

            self.slapi_print(dataframe)

    def move(self, partition, sourcebarcode, destination, wait=True):

        dataframe = self.get_inventoryfull_dataframe(partition=partition)
        rows = dataframe.query(f"mediaBarcode == '{sourcebarcode}'")
        if len(rows) == 0:
            raise(Exception(f"Error: Unable to locate barcode {sourcebarcode} in partition {partition}"))
        elif len(rows) > 1:
            raise(Exception(f"Error: Multiple rows for barcode {sourcebarcode} in partition {partition} found"))
        source = int(rows.iloc[0]["address"])

        # For now only allow drive to slot or slot to drive
        # moves, just like we used to in the old version of
        # slapi. Would be nice if the API allowed us to use
        # the barcodes for the cartridge.
        #
        # This means the tape cartridge is in a drive
        if source >= 256 and source < 4096:
            source_type = "drive"
            destination_type = "slot"
            if destination >= 256 and destination < 4096:
                raise(Exception(f"Error: Invalid drive to drive move"))
        # This means the tape cartridge is in a slot
        elif source >= 4096:
            source_type = "slot"
            destination_type = "drive"
            if destination >= 4096:
                raise(Exception(f"Error: Invalid slot to slot move"))
        else:
            raise(Exception(f"Error: Invalid move"))

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Start a media move operation
            move_request_media = lumosapi_client.MoveRequestMedia(partition=partition, source_address=source, dest_address=destination)
            api_response = api_instance.start_media_move(move_request_media)
            task_id = api_response.task_id

            if wait == True:
                self.taskwait(task_id=task_id, timeout=600, operation="media move")
                print(f"Media move for {sourcebarcode} succeeded from {source_type}: {source} to {destination_type}: {destination}.")
            else:
                print(f"Media move for {sourcebarcode} started. TaskId: {task_id}")

    def robotservice(self, robot=None, action=None, wait=True):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            if robot == "1":
                robot = "Robot:1"
            elif robot == "2":
                robot = "Robot:2"
            else:
                raise(Exception(f"Error: Invalid robotservice robot number"))

            if action.lower() == "beginservice":
                action = "BEGIN_SERVICE"
            elif action.lower() == "endservice":
                action = "END_SERVICE"
            else:
                raise(Exception(f"Error: Invalid robotservice robot action"))

            # Start the robot service action
            api_response = api_instance.start_fru_action(robot, action)
            task_id = api_response.task_id

            if wait == True:
                self.taskwait(task_id=task_id, timeout=600, operation="robot move")
                print(f"Robot move succeeded.")
            else:
                print(f"Robot move started. TaskId: {task_id}")

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
            print(f"Package {package_file} is not stored on the library.", file=sys.stderr)
            sys.exit(1)

    def packageupdate(self, package_file):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)
            package_update_request = lumosapi_client.PackageUpdateRequest(name=package_file)

            # Begin update of library
            api_response = api_instance.start_library_update(package_update_request)
            task_id = api_response.task_id

            if wait == True:
                self.taskwait(task_id=task_id, timeout=7200, operation="package update")
                print(f"Package update succeeded.")
            else:
                print(f"Package update started. TaskId: {task_id}")

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

    def securityaudit(self, wait=True):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Start a Security Audit diagnostic
            api_response = api_instance.start_library_security_audit()
            task_id = api_response.task_id

            if wait == True:
                self.taskwait(task_id=task_id, timeout=28800, operation="security audit")
                print(f"Security audit succeeded.")
            else:
                print(f"Security audit started. TaskId: {task_id}")

    def securityauditlog(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Gather Security Audit diagnostics
            api_response = api_instance.get_library_diagnostics(type=lumosapi_client.LibraryDiagnosticType.SECURITY_AUDIT, limit=1)
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc), record_path='value')
            dataframe_exploded = dataframe.explode('taskLog')
            dataframe_tasklog = dataframe_exploded.pop('taskLog')
            self.slapi_print(dataframe_tasklog)

    def spec(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get API spec from the library
            api_response = api_instance.get_api_documentation()
            pprint(api_response)

    def sysloglist(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Set the syslog settings for the library
            api_response = api_instance.get_syslog_settings()
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc))
            self.slapi_print(dataframe)

    def syslogupdate(self, syslog_server=None, syslog_port=514):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            syslog_settings = lumosapi_client.SyslogSettings(remoteServer=syslog_server, port=syslog_port)

            # Set the syslog settings for the library
            api_response = api_instance.set_syslog_settings(syslog_settings)

            # If we got here assume the syslog settings were updated successfully
            print(f"Syslog settings updated successfully.")

    def taskinfo(self, task_id):

        with lumosapi_client.ApiClient(self.configuration) as api_client:

            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get info on the specified task
            api_response = api_instance.get_task(task_id)
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc))
            self.slapi_print(dataframe)

    def tasklist(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Retrieve Task Data (max one week ago)
            start_time = (datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0) - datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
            end_time = (datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)).strftime("%Y-%m-%dT%H:%M:%SZ")

            if self.debug:
                print(f"START_TIME: {start_time}", file=sys.stderr)

            # Here we retrieve a list of all the tasks and whittle it down
            # to the tasks started over the past 7 days. The API only provides
            # us a way to see the completed tasks after a specified time
            # tasks that started before a specified time.
            api_response = api_instance.get_tasks()
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc), record_path='value')
            dataframe.pop('class')
            dataframe.pop('type')
            dataframe = dataframe.sort_values(by=['startTime'])
            dataframe_current_tasks = dataframe[dataframe['startTime'] >= start_time]
            self.slapi_print(dataframe_current_tasks)

    def taskwait(self, task_id, timeout=None, operation="operation"):

        dot_printed = False

        if timeout is not None:
            retries = int((timeout*1.0)/5.0)

        with lumosapi_client.ApiClient(self.configuration) as api_client:

            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            i = 0
            while (True):
                api_response = api_instance.get_task(task_id)
                state = api_response.state
                log = api_response.task_log
                if state == lumosapi_client.TaskStates.SUCCEEDED:
                    if self.verbose:
                        if dot_printed:
                            print("", flush=True)
                        print(f"Successfully completed {operation}")
                    return(True)
                if state == lumosapi_client.TaskStates.FAILED:
                    if self.verbose and dot_printed:
                        print("", flush=True)
                    raise(Exception(f"Error: Task {operation} failed. {api_response.result_error.message}"))
                elif timeout is not None and i >= retries:
                    if self.verbose and dot_printed:
                        print("", flush=True)
                    raise(Exception(f"Error: Timed out waiting for {operation} to complete"))
                else:
                    if self.debug:
                        print(f"{i}: {state} {api_response}", file=sys.stderr)
                    elif self.verbose:
                        print(f".", end="", flush=True)
                        dot_printed = True
                i = i+1
                time.sleep(5)

    def logdownloadrimtousb(self, rim, wait=True):
        match = re.match(r"RIM:\d+:\d+", rim)
        if not match:
            print(f"ERROR: Please make sure the RIM name has the following format: 'RIM:1:1'")
            sys.exit()
        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)
            api_response = api_instance.start_fru_action(rim, "WRITE_LOGS_TO_USB")
            
            task_id = api_response.task_id
            if wait == True:
                self.taskwait(task_id=task_id, timeout=120, operation="write rim logs to usb")
                print(f"Writing RIM logs for {rim} to USB succeeded.")
            else:
                print(f"Writing RIM logs for {rim} to USB started. TaskId: {task_id}")

    def temperaturemetrics(self):

        # Enter a context with an instance of the API client
        with lumosapi_client.ApiClient(self.configuration) as api_client:
            # Create an instance of the API class
            api_instance = lumosapi_client.TFinityApi(api_client)

            # Get the temperature metrics from the library
            # For now we only try to get the most recent reading
            # Hard code to 10 min interval 10 mins ago
            start_time = (datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0) - datetime.timedelta(seconds=600)).strftime("%Y-%m-%dT%H:%M:%SZ")
            api_response = api_instance.get_temperature_metrics(start_time=start_time, interval="10m")
            json_doc = api_response.to_json()
            dataframe = pandas.json_normalize(json.loads(json_doc))

            for column_name in dataframe.columns:
               tmp_dataframe = dataframe.pop(column_name)
               tmp_dataframe = tmp_dataframe.explode(column_name).to_frame().dropna()
               if not tmp_dataframe.empty:
                   tmp_dataframe = tmp_dataframe[column_name].apply(pandas.Series)
                   tmp_dataframe = tmp_dataframe.add_prefix(f"{column_name}.")
                   self.slapi_print(tmp_dataframe)
                   self.slapi_print(None)


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
            raise(Exception(f"create_audit_results_XML_records Error creating XML"))

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
                           help='Add debugging output (even more logging).')

    cmdparser.add_argument('--verbose', '-v', dest='verbose', action='store_true',
                           help='Add verbose output.')

    cmdparser.add_argument('--nowait', '-N', dest='wait', action='store_false',
                           help='Do not wait for long running operations.')

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

    pwaction = cmdparser.add_mutually_exclusive_group(required=False)
    pwaction.add_argument('--insecure-passwd', '-I', dest='passwd',
                          help='Password for Spectra Logic Library Login. ' +
                               'Do not use this option if you care about security. ' +
                               'Specify the password in the config file instead.')
    pwaction.add_argument('--passwd', '-p', dest='passwd_prompt', action='store_true',
                          help='Prompt user for password to Spectra Logic Library.')

    dlmlist_parser = cmdsubparsers.add_parser('dlmlist',
        help='Retrieve a list of DLM records in the library.')

    drivelist_parser = cmdsubparsers.add_parser('drivelist',
        help='Retrieve the drives in the library.')

    drivelist_parser.add_argument('partition', action='store', nargs='?',
        help='Library partition to retrieve drive information for. If the partition is omitted then all drives are returned.')

    drivesummary_parser = cmdsubparsers.add_parser('drivesummary',
        help='Get a summary of drives.')

    environmentlist_parser = cmdsubparsers.add_parser('environmentlist',
        help='Get the library environmental settings.')

    frus_parser = cmdsubparsers.add_parser('frus',
        help='Retrieve a list of hardware field replaceable units currently in the library.')

    humidity_parser = cmdsubparsers.add_parser('humidity',
        help='Get the current humidity reading from the library.')

    inventory_parser = cmdsubparsers.add_parser('inventory',
        help='Retrieve inventory from the library.')
    inventory_parser.add_argument('partition', action='store', nargs='?',
        help='Library partition to retrieve inventory for. If the partition is omitted then all partitions are returned.')


    inventoryfull_parser = cmdsubparsers.add_parser('inventoryfull',
        help='Retrieve inventory from the library (including magazine info).')
    inventoryfull_parser.add_argument('partition', action='store', nargs='?',
        help='Library partition to retrieve inventory for. If the partition is omitted then all partitions are returned.')

    librarystatus_parser = cmdsubparsers.add_parser('librarystatus',
        help='Retrieve library status information.')

    log_parser = cmdsubparsers.add_parser('log',
        help='log command help.')
    log_subparser = log_parser.add_subparsers(title="subcommands", dest="subcommand")

    log_download_parser = log_subparser.add_parser('download',
        help='Download the specified type of log from the library. e.g. motion or motion:app')
    log_download_parser.add_argument('logname', action='store',
        help='Name to use for logfile output.')
    log_download_parser.add_argument('logtype', action='store',
        help='Type of log to download. e.g. motion or motion:app')
    log_download_parser.add_argument('logdate', action='store', nargs='?',
        help='Date to gather for logfile output. The logs gathered will include the specified date and 24 hours prior.')

    log_types_parser = log_subparser.add_parser('types',
        help='List the available log types from the library.')

    log_rimtousb_parser = log_subparser.add_parser('rimtousb',
        help='Write the RIM logs to a USB. Note: This is not an official log type and can only be saved to a USB.')
    log_rimtousb_parser.add_argument('rim', action='store',
        help='Specify the RIM (Ex: RIM:1:1)')

    login_parser = cmdsubparsers.add_parser('login',
        help='Login and get tokens from the library.')

    magazines_parser = cmdsubparsers.add_parser('magazines',
        help='Retrieve magazines from the library.')
    magazines_parser.add_argument('partition', action='store', nargs='?',
        help='Library partition to retrieve magazines for. If the partition is omitted then all partitions are returned.')

    messages_parser = cmdsubparsers.add_parser('messages',
        help='Retrieve the library messages.')

    mlmlist_parser = cmdsubparsers.add_parser('mlmlist',
        help='Retrieve a list of MLM records in the library.')

    move_parser = cmdsubparsers.add_parser('move',
        help='Move tape cartridges around the library.')
    move_parser.add_argument('partition', action='store',
        help='Library partition to use for the move.')
    move_parser.add_argument('sourcebarcode', action='store',
        help='Source barcode for tape cartridge.')
    move_parser.add_argument('destination', action='store',
        type=int,
        help='Destination location to move tape cartridge to.')

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

    package_upload_parser = package_subparser.add_parser('upload',
        help='Upload a new software package to the library.')
    package_upload_parser.add_argument('package_file', action='store',
        help='Path to software package file to upload.')
    package_upload_parser.add_argument('pubkey_file', action='store',
        help='Path to software package verification file to upload.')

    robotservice_parser = cmdsubparsers.add_parser('robotservice',
        help='Send robot to/from service bay.')
    robotservice_subparser = robotservice_parser.add_subparsers(title="subcommands", dest="subcommand", required=True)

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

    securityaudit_parser = cmdsubparsers.add_parser('securityaudit',
        help='Start a new security audit on the library.')

    securityauditlog_parser = cmdsubparsers.add_parser('securityauditlog',
        help='Get the results from the latest security audit.')

    spec_parser = cmdsubparsers.add_parser('spec',
        help='Get the newest REST API spec.')

    syslog_parser = cmdsubparsers.add_parser('syslog',
        help='Syslog command help.')
    syslog_subparser = syslog_parser.add_subparsers(title="subcommands", dest="subcommand")

    syslog_list_parser = syslog_subparser.add_parser('list',
        help='List the library syslog settings.')

    syslog_update_parser = syslog_subparser.add_parser('update',
        help='Update library syslog settings.')
    syslog_update_parser.add_argument('syslog_server', action='store',
        help='Syslog server to use for the library.')
    syslog_update_parser.add_argument('syslog_port', action='store',
        type=int,
        help='Syslog port to use for the library.')

    task_parser = cmdsubparsers.add_parser('task',
        help='task command help.')
    task_subparser = task_parser.add_subparsers(title="subcommands", dest="subcommand")

    task_list_parser = task_subparser.add_parser('list',
        help='List tasks for library.')

    task_info_parser = task_subparser.add_parser('info',
        help='Get details for specified task.')
    task_info_parser.add_argument('task_id', action='store',
        help='Specific task id to get details for.')

    task_wait_parser = task_subparser.add_parser('wait',
        help='Wait for specified task to complete.')
    task_wait_parser.add_argument('task_id', action='store',
        help='Specific task id to wait for.')

    temperature_parser = cmdsubparsers.add_parser('temperature',
        help='Get the current temperature reading from the library.')

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
            raise(Exception(f"Error: SERVER not specified"))
        if args.user is None or args.user == "":
            raise(Exception(f"Error: USER not specified"))
        if args.passwd is None:
            raise(Exception(f"Error: PASSWD not specified"))
    except Exception as e:
        print(str(e))
        sys.exit(1)

    slapi = SpectraLogicAPI(args)

    while slapi.num_tries <= 1:
        try:
            if args.command is None:
                cmdparser.print_help()
                sys.exit(1)
            elif args.command == "dlmlist":
                slapi.dlmlist()
            elif args.command == "drivelist":
                slapi.drivelist(partition=args.partition)
            elif args.command == "drivesummary":
                slapi.drivesummary()
            elif args.command == "environmentlist":
                slapi.environmentlist()
            elif args.command == "frus":
                slapi.frus()
            elif args.command == "humidity":
                slapi.humiditymetrics()
            elif args.command == "inventory":
                slapi.inventory(partition=args.partition)
            elif args.command == "inventoryfull":
                slapi.inventoryfull(partition=args.partition)
            elif args.command == "librarystatus":
                slapi.librarystatus()
            elif args.command == "log":
                if args.subcommand is None or args.subcommand == "types":
                    slapi.logtypes()
                elif args.subcommand == "download":
                    slapi.logdownload(logname=args.logname, logtype=args.logtype, logdate=args.logdate)
                elif args.subcommand == "rimtousb":
                    slapi.logdownloadrimtousb(rim=args.rim)
                else:
                    raise(Exception(f"log: Unknown option {args.subcommand}"))
            elif args.command == "login":
                slapi.login()
            elif args.command == "magazines":
                slapi.magazines(partition=args.partition)
            elif args.command == "messages":
                slapi.messages()
            elif args.command == "mlmlist":
                slapi.mlmlist()
            elif args.command == "move":
                slapi.move(partition=args.partition, sourcebarcode=args.sourcebarcode, destination=args.destination, wait=args.wait)
            elif args.command == "package":
                if args.subcommand is None or args.subcommand == "list":
                    slapi.packagelist()
                elif args.subcommand == "delete":
                    slapi.packagedelete(args.package_file)
                elif args.subcommand == "update":
                    slapi.packageupdate(args.package_file)
                elif args.subcommand == "upload":
                    slapi.packageupload(args.package_file, args.pubkey_file)
                else:
                    raise(Exception(f"package: Unknown option {args.subcommand}"))
            elif args.command == "robotservice":
                slapi.robotservice(robot=args.robot, action=args.subcommand, wait=args.wait)
            elif args.command == "securityaudit":
                slapi.securityaudit(wait=args.wait)
            elif args.command == "securityauditlog":
                slapi.securityauditlog()
            elif args.command == "spec":
                slapi.spec()
            elif args.command == "syslog":
                if args.subcommand is None or args.subcommand == "list":
                    slapi.sysloglist()
                elif args.subcommand == "update":
                    slapi.syslogupdate(syslog_server=args.syslog_server, syslog_port=args.syslog_port)
                else:
                    raise(Exception(f"package: Unknown option {args.subcommand}"))
            elif args.command == "task":
                if args.subcommand is None or args.subcommand == "list":
                    slapi.tasklist()
                elif args.subcommand == "info":
                    slapi.taskinfo(task_id=args.task_id)
                elif args.subcommand == "wait":
                    slapi.taskwait(task_id=args.task_id)
                else:
                    raise(Exception("task: Unknown option {args.subcommand}"))
            elif args.command == "temperature":
                slapi.temperaturemetrics()
            else:
                cmdparser.print_help()
                sys.exit(1)

            # In the successful case we want slapi.num_tries to increment twice
            # Once here and once in the finally clause so that we are done
            # Note that slapi.login() will also increment slapi.num_tries
            slapi.num_tries = slapi.num_tries + 1

        except lumosapi_client.exceptions.UnauthorizedException as e:
            if slapi.verbose:
                print("Unauthorized...Logging in again...", file=sys.stderr)
            slapi.login()
            # If we are not logged in at this point we have a problem
            if not slapi.loggedin and slapi.num_tries >= 1:
                sys.exit(1)
        except (lumosapi_client.exceptions.ConflictException,
                lumosapi_client.exceptions.NotFoundException,
                lumosapi_client.exceptions.UnprocessableEntityException) as e:
            json_doc = json.loads(e.body)
            print(f"Error ({json_doc['error']['code']}): {json_doc['error']['message']}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            fullcommand = args.command
            if hasattr(args, "subcommand") and args.subcommand is not None:
                fullcommand = args.command + " " + args.subcommand
            print("Command '" + fullcommand + "': " + str(e), file=sys.stderr)
            if slapi.debug:
                print(type(e), file=sys.stderr)
            sys.exit(1)
        finally:
            slapi.num_tries = slapi.num_tries + 1

if __name__ == "__main__":
    main()
