#!/usr/bin/env bash
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

XRAY_URL=$1
XRAY_USER=$2
SPLUNK_URL=$3
SPLUNK_PORT=$4
SPLUNK_USER=$5
SPLUNK_VIOLATION_INDEX=$6
SPLUNK_VIOLATION_DETAIL_INDEX=$7
SPLUNK_SOURCETYPE=$8
XRAY_URL_THREAD_COUNT=$9
XRAY_PASS=""
SPLUNK_PASS=""
shift
if [[ -z "$9" ]]
then
  read -s -p "Enter Xray Password: " XRAY_PASS
  echo ""
  read -s -p "Enter Splunk Password: " SPLUNK_PASS
  echo ""
else
  # passed over command line $@
  shift
  XRAY_PASS=$8
  SPLUNK_PASS=$9
  echo "It is insecure to supply authenication credentials over the command line prompt."
  echo "Using Xray & Splunk password provided via command line."
  echo ""
fi

echo "Welcome to the Xray Splunk Integration Docker Container"
echo "This container's entrypoint.sh will process Xray Violations into the specified Splunk index"
echo "It will also call for Xray Violation Details into either the same index or a separate index"
echo ""
echo "Found the following configuration parameters supplied:"
echo "XRAY URL: ${XRAY_URL}"
echo "XRAY USER: ${XRAY_USER}"
echo "SPLUNK URL: ${SPLUNK_URL}"
echo "SPLUNK PORT: ${SPLUNK_PORT}"
echo "SPLUNK USER: ${SPLUNK_USER}"
echo "SPLUNK VIOLATION INDEX: ${SPLUNK_VIOLATION_INDEX}"
echo "SPLUNK VIOLATION DETAIL INDEX: ${SPLUNK_VIOLATION_DETAIL_INDEX}"
echo "SPLUNK SOURCETYPE: ${SPLUNK_SOURCETYPE}"
echo "XRAY URL DETAIL THREAD COUNT: ${XRAY_URL_THREAD_COUNT}"
echo ""

# BACKGROUND PROCESS THE DISPLAY SPLUNK COUNTS
( ./scripts/display_splunk_counts.py "${SPLUNK_URL}" "${SPLUNK_PORT}" "${SPLUNK_USER}" "${SPLUNK_VIOLATION_INDEX}" "${SPLUNK_VIOLATION_DETAIL_INDEX}" "${SPLUNK_PASS}")&

# RUN THE INTEGRATION INDEFINITELY IN THE CONTAINER
while true
do
  SCRIPT_RUNNING=$(ps -ef | grep xray_splunk_integration | wc -l)
  if [[ "$SCRIPT_RUNNING" =~ (1) ]]
  then
    ./scripts/xray_splunk_integration.py "${XRAY_URL}" "${XRAY_USER}" "${SPLUNK_URL}" "${SPLUNK_PORT}" "${SPLUNK_USER}" "${SPLUNK_VIOLATION_INDEX}" "${SPLUNK_VIOLATION_DETAIL_INDEX}" "${SPLUNK_SOURCETYPE}" "${XRAY_URL_THREAD_COUNT}" "${XRAY_PASS}" "${SPLUNK_PASS}"
    sleep 15
  else
    sleep 30
  fi

  # VERIFY THAT THE COUNT DISPLAY IS STILL RUNNING IF NOT RESTART IT
  SCRIPT_RUNNING=$(ps -ef | grep display_splunk_counts | wc -l)
  if [[ "$SCRIPT_RUNNING" =~ (1) ]]
  then
    ( ./scripts/display_splunk_counts.py "${SPLUNK_URL}" "${SPLUNK_PORT}" "${SPLUNK_USER}" "${SPLUNK_VIOLATION_INDEX}" "${SPLUNK_VIOLATION_DETAIL_INDEX}" "${SPLUNK_PASS}")&
  fi
done
