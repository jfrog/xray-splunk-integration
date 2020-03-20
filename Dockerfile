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
FROM ubuntu:18.04
USER root
MAINTAINER johnp@jfrog.com

# Update image
RUN apt-get upgrade -y
RUN apt-get update -y

# Install required packages
RUN apt-get install python3.6 python3-pip wget curl git -y
RUN pip3 install requests
RUN pip3 install datetime
RUN pip3 install splunk-sdk

# Assign working directory
RUN mkdir -p /root/workdir
RUN mkdir -p /root/workdir/logs
RUN mkdir -p /root/workdir/scripts
WORKDIR /root/workdir

# Download Splunk Python SDK and add to PYTHONPATH
RUN git clone https://github.com/splunk/splunk-sdk-python.git
ENV PYTHONPATH /root/workdir/splunk-sdk-python

# Copy over script into working directory
COPY scripts/xray_splunk_integration.py /root/workdir/scripts/xray_splunk_integration.py
COPY scripts/display_splunk_counts.py /root/workdir/scripts/display_splunk_counts.py
COPY scripts/entrypoint.sh /root/workdir/scripts/entrypoint.sh

ENTRYPOINT ["/root/workdir/scripts/entrypoint.sh"]
