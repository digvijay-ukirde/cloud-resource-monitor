import argparse
from ibmcloud.auth.iam import get_access_token
from utils.common import logger, set_debug_mode, read_json_file
from utils.elasticsearch import check_connection, delete_older_data, upload_data
from ibmcloud.vpc.regions import get_regions_map
from ibmcloud.vpc.vpcs import get_vpc_list
from ibmcloud.vpc.instances import get_instance_list, get_instance_ini_conf
from ibmcloud.vpc.bare_metal_servers import get_bare_metal_server_list, get_bare_metal_server_ini_conf
from ibmcloud.vpc.images import get_image_list
from ibmcloud.vpc.volumes import get_volume_list
from ibmcloud.vpc.floating_ips import get_floating_ip_list
from ibmcloud.vpc.dedicated_hosts import get_dedicated_host_list
from ibmcloud.outputs.vpc import set_vpc_details, set_instance_details, set_bare_metal_server_details, \
    set_image_details, set_volume_details, set_floating_ip_details, set_dedicated_host_details

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description='Retrieve resource information')
    SUBPARSERS = PARSER.add_subparsers(dest='platform', required=True, help='Cloud infrastructure platform')
    aws_parser = SUBPARSERS.add_parser('aws', help='AWS cloud infrastructure platform')
    aws_parser.add_argument('--access-key-id', required=True, help='AWS access key')
    aws_parser.add_argument('--secret-access-key', required=True, help='AWS secret access key')
    ibmcloud_parser = SUBPARSERS.add_parser('ibmcloud', help='IBMCloud cloud infrastructure platform')
    ibmcloud_parser.add_argument('--api-key', required=True, help='IBM Cloud API key')
    PARSER.add_argument('--account', required=True, help='Unique name/id for IBM Cloud account')
    PARSER.add_argument('--metadata', help='Json file consist of Metadata (key=value) to tag resources')
    PARSER.add_argument('--owner-map', help='Json file consist of Owner mapping to the resources')
    PARSER.add_argument('--elastic', help='Json file consist of ElasticSearch configuration')
    PARSER.add_argument('--debug', default=False, help='Debug mode')
    ARGUMENTS = PARSER.parse_args()
    logger.info(f"Retrieve resource information from {ARGUMENTS.platform} - {ARGUMENTS.account} account.")

    if ARGUMENTS.debug:
        set_debug_mode()
    metadata = {'platform': ARGUMENTS.platform, 'account': ARGUMENTS.account}
    if ARGUMENTS.metadata:
        meta_data = read_json_file(ARGUMENTS.metadata)
        metadata.update(meta_data)
    if ARGUMENTS.owner_map:
        owner_map = read_json_file(ARGUMENTS.owner_map)
    else:
        owner_map = None
    elastic_client = None
    if ARGUMENTS.elastic:
        elastic_client = check_connection(ARGUMENTS.elastic)
        delete_older_data(elastic_client, metadata)

    if ARGUMENTS.platform == 'ibmcloud':
        access_token = get_access_token(ARGUMENTS.api_key)

        regions_map = get_regions_map()
        for region_id, region_name in regions_map.items():
            metadata['region'] = region_name

            vpc_list = get_vpc_list(access_token, region_id)
            instance_list = get_instance_list(access_token, region_id)
            bare_metal_server_list = get_bare_metal_server_list(access_token, region_id)
            image_list = get_image_list(access_token, region_id)
            volume_list = get_volume_list(access_token, region_id)
            floating_ip_list = get_floating_ip_list(access_token, region_id)
            dedicated_host_list = get_dedicated_host_list(access_token, region_id)

            try:
                if 'vpcs' in vpc_list:
                    for vpc in vpc_list['vpcs']:
                        vpc_details = set_vpc_details(vpc)
                        vpc_details.update(metadata)
                        if elastic_client:
                            upload_data(elastic_client, vpc_details)
            except ValueError as err:
                logger.warning(f"Obtaining VPC list failed. Value Error : {err}. Skipping!")
            except TypeError as err:
                logger.warning(f"Obtaining VPC list failed. Type Error : {err}. Skipping!")

            try:
                if 'instances' in instance_list:
                    for instance in instance_list['instances']:
                        instance['key'], instance['owner'] = get_instance_ini_conf(access_token, region_id,
                                                                                   instance['id'], owner_map)
                        if instance['owner'] == 'Unknown':
                            logger.warning(f"Owner not found for {instance['name']} instance "
                                           f"with {instance['key']} in {region_name} region.")
                        instance_details = set_instance_details(instance)
                        instance_details.update(metadata)
                        if elastic_client:
                            upload_data(elastic_client, instance_details)
            except ValueError as err:
                logger.warning(f"Obtaining instance list failed. Value Error : {err}. Skipping!")
            except TypeError as err:
                logger.warning(f"Obtaining instance list failed. Type Error : {err}. Skipping!")

            try:
                if 'bare_metal_servers' in bare_metal_server_list:
                    for bare_metal_server in bare_metal_server_list['bare_metal_servers']:
                        bare_metal_server['key'], bare_metal_server['owner'] = \
                            get_bare_metal_server_ini_conf(access_token, region_id, bare_metal_server['id'], owner_map)
                        if bare_metal_server['owner'] == 'Unknown':
                            logger.warning(f"Owner not found for {bare_metal_server['name']} bare metal server "
                                           f"with {bare_metal_server['key']} in {region_name} region.")
                        bare_metal_server_details = set_bare_metal_server_details(bare_metal_server)
                        bare_metal_server_details.update(metadata)
                        if elastic_client:
                            upload_data(elastic_client, bare_metal_server_details)
            except ValueError as err:
                logger.warning(f"Obtaining bare metal server list failed. Value Error : {err}. Skipping!")
            except TypeError as err:
                logger.warning(f"Obtaining bare metal server list failed. Type Error : {err}. Skipping!")

            try:
                if 'images' in image_list:
                    for image in image_list['images']:
                        if image['visibility'] != 'public':
                            image_details = set_image_details(image)
                            image_details.update(metadata)
                            if elastic_client:
                                upload_data(elastic_client, image_details)
            except ValueError as err:
                logger.warning(f"Obtaining image list failed. Value Error : {err}. Skipping!")
            except TypeError as err:
                logger.warning(f"Obtaining image list failed. Type Error : {err}. Skipping!")

            try:
                if 'volumes' in volume_list:
                    for volume in volume_list['volumes']:
                        volume_details = set_volume_details(volume)
                        volume_details.update(metadata)
                        if elastic_client:
                            upload_data(elastic_client, volume_details)
            except ValueError as err:
                logger.warning(f"Obtaining volume list failed. Value Error : {err}. Skipping!")
            except TypeError as err:
                logger.warning(f"Obtaining volume list failed. Type Error : {err}. Skipping!")

            try:
                if 'floating_ips' in floating_ip_list:
                    for floating_ip in floating_ip_list['floating_ips']:
                        floating_ip_details = set_floating_ip_details(floating_ip)
                        floating_ip_details.update(metadata)
                        if elastic_client:
                            upload_data(elastic_client, floating_ip_details)
            except ValueError as err:
                logger.warning(f"Obtaining floating IP list failed. Value Error : {err}. Skipping!")
            except TypeError as err:
                logger.warning(f"Obtaining floating IP list failed. Type Error : {err}. Skipping!")

            try:
                if 'dedicated_hosts' in dedicated_host_list:
                    for dedicated_host in dedicated_host_list['dedicated_hosts']:
                        dedicated_host_details = set_dedicated_host_details(dedicated_host)
                        dedicated_host_details.update(metadata)
                        if elastic_client:
                            upload_data(elastic_client, dedicated_host_details)
            except ValueError as err:
                logger.warning(f"Obtaining dedicated hosts list failed. Value Error : {err}. Skipping!")
            except TypeError as err:
                logger.warning(f"Obtaining dedicated hosts list failed. Type Error : {err}. Skipping!")
