#!/usr/bin/env python3
#
# Copyright 2020 JFrog, LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import logging
import json
import html
import requests
import sys
import datetime
import os.path
from os import path
from splunklib.client import connect
import splunklib.results as results
import time

########################################################################
# GLOBAL VARIABLES
########################################################################
splunk_url, splunk_port, splunk_user, splunk_pass = "", 0, "", ""
splunk_violations_indexname, splunk_details_indexname = "", ""

########################################################################
# FUNCTIONS
########################################################################

# verifies the correct number of command line args were specified
def input_arg_check():
    # Get arguments
    if  (len(sys.argv) != 7):
        exit()

    if (len(sys.argv[1]) == 0):
        exit()

def query_splunk_index_count(service, index_name):
    splunk_index = service.indexes[index_name]
    searchquery = "search * index=\"" + index_name + "\" | stats count as totalCount"
    oneshotsearch_results = service.jobs.oneshot(searchquery)

    # Get the last splunk item or default to UNIX epoch
    reader = results.ResultsReader(oneshotsearch_results)
    count = 0
    for item in reader:
        count=item['totalCount']
        break
    return count


########################################################################
# MAIN
########################################################################

# verify and assign input args
input_arg_check()
splunk_url = sys.argv[1]
splunk_port = sys.argv[2]
splunk_user = sys.argv[3]
splunk_violations_indexname = sys.argv[4]
splunk_details_indexname = sys.argv[5]
splunk_pass = sys.argv[6]


# Connect to the splunk server
service = connect(
            host=splunk_url,
            port=splunk_port,
            username=splunk_user,
            password=splunk_pass)

while True:
    time.sleep(30)
    violationsCount=query_splunk_index_count(service, splunk_violations_indexname)
    detailsCount=query_splunk_index_count(service, splunk_details_indexname)
    print("Number of violations processed: " + violationsCount)
    print("Number of violation details processed: " + detailsCount)