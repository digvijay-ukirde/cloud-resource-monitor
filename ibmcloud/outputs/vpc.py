from datetime import datetime
import math
from utils.common import logger, write_json_file, write_elk_file, read_json_file


def get_resource_age(creation_date):
    t_day = datetime.utcnow()
    c_day = datetime.strptime(creation_date[:19], "%Y-%m-%dT%H:%M:%S")
    age = t_day - c_day
    logger.debug(f"Resource Age: {age}")
    return age.days


def get_resource_cost(resource_details):
    cost = 0
    file_path = f"ibmcloud/vpc/resource_cost_sheet.json"
    cost_sheet_details = read_json_file(file_path)
    c_day = datetime.strptime(resource_details['created_at'][:19], "%Y-%m-%dT%H:%M:%S")
    t_day = datetime.utcnow()
    age = t_day - c_day
    logger.debug(f"Resource Age: {age}")
    total_hrs = math.ceil(age.total_seconds()/3600)
    logger.debug(f"Resource Billable hours: {total_hrs}")
    logger.debug(f"Resource type is {resource_details['resource_type']}")
    if resource_details['resource_type'] in ['Instance', 'Bare Metal Server', 'Dedicated Host']:
        if resource_details['profile']:
            logger.debug(f"Resource profile is {resource_details['profile']}")
            if cost_sheet_details[resource_details['resource_type']][resource_details['profile']]:
                cost = total_hrs * cost_sheet_details[resource_details['resource_type']][resource_details['profile']]
            else:
                cost = 0
    return round(cost, 2)


def get_disk_details(disks):
    count = 0
    size = 0
    total_storage = 0
    for disk in disks:
        count = count + 1
        size = disk['size']
        total_storage = total_storage + disk['size']
    return count, size, total_storage


def set_vpc_details(vpc):
    vpc_details = {
        'resource_type': 'VPC',
        'id': vpc['id'],
        'name': vpc['name'],
        'href': vpc['href'],
        'resource_group': vpc['resource_group']['name'],
        'status': vpc['status'],
        'created_at': vpc['created_at'],
        'cost': 0
    }
    vpc_details['age'] = get_resource_age(vpc_details['created_at'])
    logger.debug(f"VPC Details: {vpc_details}")
    if logger.root.level == logger.DEBUG:
        file_name = f"data/vpc-{vpc_details['name']}.json"
        write_json_file(file_name, vpc_details)
        write_elk_file('data/vpcs.json', vpc_details)
    return vpc_details


def set_instance_details(instance):
    instance_details = {
        'resource_type': 'Instance',
        'id': instance['id'],
        'name': instance['name'],
        'href': instance['href'],
        'zone': instance['zone']['name'],
        'vpc_id': instance['vpc']['id'],
        'vpc_name': instance['vpc']['name'],
        'resource_group': instance['resource_group']['name'],
        'status': instance['status'],
        'created_at': instance['created_at'],
        'image_id': instance['image']['id'],
        'image_name': instance['image']['name'],
        'key': instance['key'],
        'owner': instance['owner'],
        'profile': instance['profile']['name'],
        'vcpu': instance['vcpu']['count'],
        'memory': instance['memory'],
        'bandwidth': instance['bandwidth'],
        'network_bandwidth': instance['total_network_bandwidth'],
        'volume_bandwidth': instance['total_volume_bandwidth'],
        'metadata_service_enabled': instance['metadata_service']['enabled']
    }
    instance_details['age'] = get_resource_age(instance_details['created_at'])
    instance_details['cost'] = get_resource_cost(instance_details)
    try:
        if 'disks' in instance:
            instance_details['disk_count'], instance_details['disk_size'], instance_details['total_storage'] = \
                get_disk_details(instance['disks'])
    except ValueError as err:
        logger.warning(f"Obtaining disk list failed. Value Error : {err}. Skipping!")
    except TypeError as err:
        logger.warning(f"Obtaining disk list failed. Type Error : {err}. Skipping!")
    logger.debug(f"Instance Details: {instance_details}")
    if logger.root.level == logger.DEBUG:
        file_name = f"data/instance-{instance_details['name']}.json"
        write_json_file(file_name, instance_details)
        write_elk_file('data/instances.json', instance_details)
    return instance_details


def set_bare_metal_server_details(bare_metal_server):
    bare_metal_server_details = {
        'resource_type': 'Bare Metal Server',
        'id': bare_metal_server['id'],
        'name': bare_metal_server['name'],
        'href': bare_metal_server['href'],
        'zone': bare_metal_server['zone']['name'],
        'vpc_id': bare_metal_server['vpc']['id'],
        'vpc_name': bare_metal_server['vpc']['name'],
        'resource_group': bare_metal_server['resource_group']['name'],
        'status': bare_metal_server['status'],
        'created_at': bare_metal_server['created_at'],
        'key': bare_metal_server['key'],
        'owner': bare_metal_server['owner'],
        'profile': bare_metal_server['profile']['name'],
        'vcpu': bare_metal_server['cpu']['core_count'] * bare_metal_server['cpu']['threads_per_core'],
        'memory': bare_metal_server['memory'],
        'bandwidth': bare_metal_server['bandwidth']
    }
    bare_metal_server_details['age'] = get_resource_age(bare_metal_server_details['created_at'])
    bare_metal_server_details['cost'] = get_resource_cost(bare_metal_server_details)

    try:
        if 'disks' in bare_metal_server:
            bare_metal_server_details['disk_count'], bare_metal_server_details['disk_size'], \
                bare_metal_server_details['total_storage'] = get_disk_details(bare_metal_server['disks'])
    except ValueError as err:
        logger.warning(f"Obtaining disk list failed. Value Error : {err}. Skipping!")
    except TypeError as err:
        logger.warning(f"Obtaining disk list failed. Type Error : {err}. Skipping!")
    logger.debug(f"Bare metal server Details: {bare_metal_server_details}")
    if logger.root.level == logger.DEBUG:
        file_name = f"data/bare_metal_server-{bare_metal_server_details['name']}.json"
        write_json_file(file_name, bare_metal_server_details)
        write_elk_file('data/bare_metal_server.json', bare_metal_server_details)
    return bare_metal_server_details


def set_dedicated_host_details(dedicated_host):
    dedicated_host_details = {
        'resource_type': 'Dedicated Host',
        'id': dedicated_host['id'],
        'name': dedicated_host['name'],
        'href': dedicated_host['href'],
        'resource_group': dedicated_host['resource_group']['name'],
        'status': dedicated_host['state'],
        'created_at': dedicated_host['created_at'],
        'zone': dedicated_host['zone']['name'],
        'socket_count': dedicated_host['socket_count'],
        'provisionable': dedicated_host['provisionable'],
        'lifecycle_state': dedicated_host['lifecycle_state'],
        'instance_placement_enabled': dedicated_host['instance_placement_enabled'],
        'profile': dedicated_host['profile']['name'],
        'vcpu': dedicated_host['vcpu']['count'],
        'memory': dedicated_host['memory']
    }
    dedicated_host_details['age'] = get_resource_age(dedicated_host_details['created_at'])
    dedicated_host_details['cost'] = get_resource_cost(dedicated_host_details)
    logger.debug(f"Dedicated Host Details: {dedicated_host_details}")
    if logger.root.level == logger.DEBUG:
        file_name = f"data/dedicated_host-{dedicated_host_details['name']}.json"
        write_json_file(file_name, dedicated_host_details)
        write_elk_file('data/dedicated_hosts.json', dedicated_host_details)
    return dedicated_host_details


def set_image_details(image):
    image_details = {
        'resource_type': 'Image',
        'id': image['id'],
        'name': image['name'],
        'href': image['href'],
        'resource_group': image['resource_group']['name'],
        'status': image['status'],
        'created_at': image['created_at'],
        'visibility': image['visibility'],
        'encryption': image['encryption'],
        'catalog_offering': image['catalog_offering']['managed'],
        'operating_system': image['operating_system']['name'],
        'architecture': image['operating_system']['architecture'],
        'cost': 0
    }
    image_details['age'] = get_resource_age(image_details['created_at'])
    logger.debug(f"Image Details: {image_details}")
    if logger.root.level == logger.DEBUG:
        file_name = f"data/image-{image_details['name']}.json"
        write_json_file(file_name, image_details)
        write_elk_file('data/image.json', image_details)
    return image_details


def set_volume_details(volume):
    volume_details = {
        'resource_type': 'Volume',
        'id': volume['id'],
        'name': volume['name'],
        'href': volume['href'],
        'resource_group': volume['resource_group']['name'],
        'status': volume['status'],
        'active': volume['active'],
        'bandwidth': volume['bandwidth'],
        'busy': volume['busy'],
        'capacity': volume['capacity'],
        'encryption': volume['encryption'],
        'iops': volume['iops'],
        'profile': volume['profile']['name'],
        'cost': 0
    }
    volume_details['age'] = get_resource_age(volume_details['created_at'])
    logger.debug(f"Volume Details: {volume_details}")
    if logger.root.level == logger.DEBUG:
        file_name = f"data/volume-{volume_details['name']}.json"
        write_json_file(file_name, volume_details)
        write_elk_file('data/image.json', volume_details)
    return volume_details


def set_floating_ip_details(floating_ip):
    floating_ip_details = {
        'resource_type': 'Floating IP',
        'id': floating_ip['id'],
        'name': floating_ip['name'],
        'href': floating_ip['href'],
        'resource_group': floating_ip['resource_group']['name'],
        'status': floating_ip['status'],
        'created_at': floating_ip['created_at'],
        'address': floating_ip['address'],
        'zone': floating_ip['zone']['name'],
        'cost': 0
    }
    floating_ip_details['age'] = get_resource_age(floating_ip_details['created_at'])
    floating_ip_details['cost'] = round((floating_ip_details['age'] / 30), 2)
    try:
        if 'target' in floating_ip:
            floating_ip_details['state'] = True
        else:
            floating_ip_details['state'] = False
    except ValueError as err:
        logger.warning(f"Obtaining floating IP list failed. Value Error : {err}. Skipping!")
    except TypeError as err:
        logger.warning(f"Obtaining floating IP list failed. Type Error : {err}. Skipping!")
    logger.debug(f"Floating IP Details: {floating_ip_details}")
    if logger.root.level == logger.DEBUG:
        file_name = f"data/floating_ip-{floating_ip_details['name']}.json"
        write_json_file(file_name, floating_ip_details)
        write_elk_file('data/floating_ips.json', floating_ip_details)
    return floating_ip_details
