# DEPRECATION NOTICE!

This effort has been merged into the overall log analytic solutions for Splunk, Elastic, Datadog, and Prometheus.

Follow the Fluentd setup for your log provider [here.](https://www.github.com/jfrog/log-analytics)

Configuration options for SIEM plugin in Log Analytics available [here.](https://github.com/jfrog/log-analytics/blob/master/fluentd/plugins/input/fluent-plugin-jfrog-siem/README.md)

Using the new version of the integration will enable the common data model mapping into SIEM for the relevant log provider such as Splunk or Elastic.


# Xray Splunk Integration
This project will integrate xray violations into splunk to be consumed as part of the data lake.
The goal of this project is only to provide the data to splunk in a reliable and consistent manner.
Once the data is delivered to splunk customers will be required to consume the data however they desire.
The data will be delivered in a JSON format to easy consumption in splunk however any specific consumption is beyond the scope of this project.

## Setup

Xray setup required:

```
Obtain URL of API
Obtain username & password for API
```

Splunk setup required:
```
Obtain URL and Port for Splunk
Obtain username & password for Splunk API
```

Splunk index setup:

Create the indexes to hold the violation and violation details data:

If you have existing indexes you want to use you can skip creating new ones.

```
violations
violation_details
```

## Getting Started 

The preferred way to run this integration is through Docker.

Assuming you have docker installed on the host machine you can run:

```
docker build -t xray_splunk_integration .
docker run -a stderr -a stdout -it xray_splunk_integration <xray_url> <xray_user> <splunk_url> <splunk_port> <splunk_user> <splunk_index> <splunk_detail_index> <splunk_sourcetype> <xray_url_thread_count>
```

It will then prompt you to enter the Xray user password and Splunk user password.

This will then run the entrypoint that will keep the integration and display count script alive.

If one of the scripts does happen to die the entrypoint will restart it for you.
 
If the container happens to die you can simply re-run the docker command to begin where you left off.

The container will run two scripts one to pull the violations and details to save them into splunk:

```
scripts/xray_splunk_integration.py
```

The second script runs a stat script to display the current counts of the two specified indexes being used to store data:

``` 
scripts/display_splunk_counts.py
```

### Local Build

To run the Xray Splunk integration locally you will need Python 3.x+ with the following pip packages installed:

Python 3.x+
```
apt-get install python3.6 python3-pip -y
```

Pip3
```
pip3 install requests
pip3 install datetime
pip3 install futures
```

[Splunk Python SDK](https://github.com/splunk/splunk-sdk-python)
```
  cd ~
  git clone git@github.com:splunk/splunk-sdk-python.git
  export PYTHONPATH=$PYTHONPATH:~/splunk-sdk-python
```

### Demo

To run this as a demo please create a new Orbitera trial of JFrog Xray available [here](https://jfrog2.orbitera.com/c2m/trials/signup?testDrive=1170&goto=%2Fc2m%2Ftrial%2F1170)

Once your environment has been created you will receive an email with the URL to Xray & admin account password.

Next you will need a splunk environment to upload the xray violation data into. Please download Splunk enterprise trail and install it locally. Run splunk and setup the admin account password.

Once you have Xray and Splunk environments up you can then run the container:

```
docker run -a stderr -a stdout -it xray_splunk_integration <xray_url> <xray_user> <splunk_url> <splunk_port> <splunk_user> <splunk_index> <splunk_detail_index> <splunk_sourcetype> <xray_url_thread_count>
```

This will start the siphon from Xray and upload the data into Splunk.


### Persistence between runs

The integration inserts records in Splunk.

The integration script will query Splunk for the latest created date of the last record processed.

It will then use this in all subsequent filters to Xray to pull data.

If there happens to be multiple records per second an additional existence check query will be run on Splunk per record at this second and only insert records into Splunk that do not already exist in the specified index.

## Running the integration

To run the integration you will need to download and install Docker.

Once you have docker installed you can run the integration with this command:

```
docker run -a stderr -a stdout -it xray_splunk_integration <xray_url> <xray_user> <splunk_url> <splunk_port> <splunk_user> <splunk_index> <splunk_detail_index> <splunk_sourcetype> <xray_url_thread_count>
```

The following args will need to be specified:

```
xray_url: the url of the xray instance to pull violations down
xray_user: the username to be used for auth against xray instance
splunk_url: the splunk url to upload the xray violation data into
splunk_port: the port to be used to connect to splunk with
splunk_user: the user to be used for auth against splunk instance
splunk_index: the index on splunk to write this data into for the violation records
splunk_detail_index: the index on splunk to write this data into for the violation detail records
splunk_sourcetype: the source type to be given to this data stream in splunk
xray_url_thread_count: integer value of the number of concurrent threads to read xray violation details url
```

Optionally you can pass at the end:

``` 
xray_pass: the password of the xray user supplied insecurely via CLI
splunk_pass: the password of the splunk user supplied insecurely via CLI
```


### Tools
* [Docker](https://www.docker.com/) - Docker container environment
* [Splunk Python SDK](https://github.com/splunk/splunk-sdk-python) - Splunk Python SDK used to upload data into Splunk

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning
We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Contact
* Github
