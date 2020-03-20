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
from concurrent.futures.thread import ThreadPoolExecutor
from splunklib.client import connect
import splunklib.results as results

########################################################################
# GLOBAL VARIABLES
########################################################################
xray_url, xray_user, xray_pass = "", "", ""
splunk_url, splunk_port, splunk_user, splunk_pass = "", 0, "", ""
splunk_indexname, splunk_detail_indexname, sourcetype = "", "", ""
jumps = 25
log_file='./logs/xray_splunk_integration.log'

########################################################################
# FUNCTIONS
########################################################################

# setups logging configuration
def setup_logging(logfile,loglevel):
    # logging.DEBUG
    logging.basicConfig(filename=logfile,level=loglevel)

# verifies the correct number of command line args were specified
def input_arg_check():
    # Get arguments
    if  (len(sys.argv) != 12):
        errorMsg="Required args: <xray_url> <xray_user> <splunk_url> <splunk_port> <splunk_user> <splunk_violation_index> <splunk_detail_index> <splunk_sourcetype> <thread_count> <xray_pass> <splunk_pass>"
        print(errorMsg)
        logging.error(errorMsg)
        exit()

    if (len(sys.argv[1]) == 0):
        errorMsg="Required args: <xray_url> <xray_user> <splunk_url> <splunk_port> <splunk_user> <splunk_violation_index> <splunk_detail_index> <splunk_sourcetype> <thread_count> <xray_pass> <splunk_pass>"
        print(errorMsg)
        logging.error(errorMsg)
        exit()

# queries the xray API for violations based upon the input json
def get_xray_violations_detail(xray_violation_url):
    resp = requests.get(xray_violation_url, auth=(xray_user,xray_pass))
    if resp.status_code != 200:
        errorMsg="{} error pulling xray violations ".format(resp.status_code)
        print(errorMsg)
        logging.error(errorMsg)
        exit()
    return resp

def check_if_splunk_item_exists(service, index_name, json):
    splunk_index = service.indexes[index_name]
    searchquery = "search \"" + html.escape(json) + "\" index=\"" + index_name + "\" | head 1"
    oneshotsearch_results = service.jobs.oneshot(searchquery)

    # Get the last splunk item or default to UNIX epoch
    reader = results.ResultsReader(oneshotsearch_results)
    exists = False
    for item in reader:
        exists = True
        break
    return exists

# queries the xray API for violations based upon the input json
def get_xray_violations(xray_json):
    resp = requests.post(xray_url + "/v1/violations", auth=(xray_user,xray_pass),json=xray_json)
    if resp.status_code != 200:
        errorMsg="{} error pulling xray violations ".format(resp.status_code)
        print(errorMsg)
        logging.error(errorMsg)
        exit()
    return resp

def get_last_splunk_item_create_date(service, index_name):
    splunk_index = service.indexes[index_name]
    searchquery = "search * index=\"" + index_name + "\" | head 1"
    oneshotsearch_results = service.jobs.oneshot(searchquery)

    # Get the last splunk item or default to UNIX epoch
    created_date="1970-01-01T00:00:00Z"
    reader = results.ResultsReader(oneshotsearch_results)
    for json_data in reader:
        if len(str(json_data['_raw'])) > 0:
            try:
                innerJson = json_data['_raw']
                parsed_json = json.loads(innerJson)
                created_date = parsed_json['created']
            except:
                created_date="1970-01-01T00:00:00Z"
    return created_date


def store_in_splunk(xray_violations_url, service, splunk_indexname, sourcetype):
    splunk_index = service.indexes[splunk_indexname]
    try:
        detailResp=get_xray_violations_detail(xray_violations_url)

        # Check to ensure this resp is not identical to the item itself
        persistItem = True

        # Determine if we need to persist this record or not
        if check_if_splunk_item_exists(service, splunk_indexname, json.dumps(detailResp.json())):
            persistItem = False

        # Save the record to the splunk index
        if persistItem:
            splunk_index.submit(event=json.dumps(detailResp.json()),sourcetype=sourcetype)

    except:
        print("Error pulling violation detail url = " + xray_violations_url)

########################################################################
# MAIN
########################################################################

# setup logging
setup_logging(log_file,logging.DEBUG)

# verify and assign input args
input_arg_check()
xray_url = sys.argv[1]
xray_user = sys.argv[2]
splunk_url = sys.argv[3]
splunk_port = sys.argv[4]
splunk_user = sys.argv[5]
splunk_indexname = sys.argv[6]
splunk_detail_indexname = sys.argv[7]
sourcetype = sys.argv[8]
thread_count = int(sys.argv[9])
xray_pass = sys.argv[10]
splunk_pass = sys.argv[11]

if thread_count > jumps:
    print("Xray Splunk Integration allows you to specify how many violation detail urls to pull concurrently.")
    print("Violation Detail Url thread count should be less than ", jumps)
    print("Please specify a lower thread count to run the integration.")
    logging.error("Violation detail url thread count exceeds batch size ", jumps)
    exit(1)

# Connect to the splunk server
service = connect(
            host=splunk_url,
            port=splunk_port,
            username=splunk_user,
            password=splunk_pass)

splunk_index = service.indexes[splunk_indexname]

# SPLUNK CONFIG INDEX USED FOR DURABLILITY ACROSS SCRIPT RUNS
last_created_date_string=get_last_splunk_item_create_date(service, splunk_indexname)

# Load last created date and splunk configs
last_created_date=datetime.datetime.strptime(last_created_date_string,"%Y-%m-%dT%H:%M:%SZ")

# Grab the first batch of records
offset_count=1
xray_json={"filters": { "created_from": last_created_date_string }, "pagination": {"order_by": "created","limit": jumps ,"offset": offset_count } }
resp=get_xray_violations(xray_json)
number_of_violations = resp.json()['total_violations']

if number_of_violations != jumps:
    logging.info('Xray Splunk Integration total number of records to process: ' +  str(number_of_violations))
    print('Xray Splunk Integration total number of records to process: ', number_of_violations)

left_violations = number_of_violations
# iterate through this batch of violations and insert them into splunk
while left_violations > 0:
    xray_violation_urls_list = []
    for index in range (0, len(resp.json()['violations'])):
        # Get the violation
        item = resp.json()['violations'][index]

        # Get the created date and check if we should skip (already processed) or process this record.
        created_date_string = item['created']
        created_date = datetime.datetime.strptime(created_date_string,"%Y-%m-%dT%H:%M:%SZ")
        # Determine if we need to persist this record or not
        persistItem = True
        if created_date < last_created_date:
            persistItem = False
        elif check_if_splunk_item_exists(service, splunk_indexname, json.dumps(item)):
            persistItem = False
        elif number_of_violations == jumps:
            # cover the case of when we keep getting last record batch w/ same create date looping forever
            if last_created_date_string == created_date_string:
                persistItem = False

        # Save the record to the splunk index
        if persistItem:
            splunk_index.submit(event=json.dumps(item),sourcetype=sourcetype)
            # Mark this as the last record successfully processed
            last_created_date_string = created_date_string
            last_created_date = created_date
            # Grab violation detail url and add to url list to process w/ thread pool
            xray_violations_url=item['violation_details_url']
            xray_violation_urls_list.append(xray_violations_url)

    # iterate over url array adding to thread pool each url.
    # limit max workers to thread count to prevent overloading xray.
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        for i in range(len(xray_violation_urls_list)):
            executor.submit(store_in_splunk, xray_violation_urls_list[i], service, splunk_detail_indexname, sourcetype)

    # reduce left violations by jump size (not all batches have full item count??)
    left_violations = left_violations - jumps
    if left_violations <= 0:
        exit()

    # Grab the next record to process for the violation details url
    offset_count = offset_count + 1
    xray_json={"filters": { "created_from": last_created_date_string }, "pagination": {"order_by": "created","limit": jumps , "offset" : offset_count } }
    resp=get_xray_violations(xray_json)
