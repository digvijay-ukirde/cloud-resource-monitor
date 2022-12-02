# cloud-resource-monitor
Utility to monitor hybrid cloud resources with single dashboard

## Usage
```
usage: main.py [-h] --account ACCOUNT [--metadata METADATA] [--owner-map OWNER_MAP] [--elastic ELASTIC] [--debug DEBUG] {aws,ibmcloud} ...

Retrieve resource information

positional arguments:
  {aws,ibmcloud}        Cloud infrastructure platform
    aws                 AWS cloud infrastructure platform
    ibmcloud            IBMCloud cloud infrastructure platform

optional arguments:
  -h, --help            show this help message and exit
  --account ACCOUNT     Unique name/id for IBM Cloud account
  --metadata METADATA   Json file consist of Metadata (key=value) to tag resources
  --owner-map OWNER_MAP
                        Json file consist of Owner mapping to the resources
  --elastic ELASTIC     Json file consist of ElasticSearch configuration
  --debug DEBUG         Debug mode
```