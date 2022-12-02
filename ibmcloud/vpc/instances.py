import datetime
from utils.common import logger
from utils.common import curl_execution
from utils.common import write_json_file


def get_instance_list(access_token, region):
    url = f"https://{region}.iaas.cloud.ibm.com/v1/instances?limit=100&version=2022-10-18&generation=2"
    headers = {'Authorization': access_token}
    out = curl_execution('get', url, headers, None)
    logger.debug(f"cURL output for listing instances: {out}")
    try:
        if 'instances' in out:
            if 'next' in out:
                while out['next']:
                    url = f"{out['next']['href']}&version=2022-10-18&generation=2"
                    logger.debug(f"Updated URL: {url}")
                    next_out = curl_execution('get', url, headers, None)
                    logger.debug(f"cURL output for new instances: {next_out}")
                    if 'instances' in next_out:
                        for instance in next_out['instances']:
                            out['instances'].append(instance)
                        if 'next' in next_out:
                            out['next'] = next_out['next']
                        else:
                            out['next'] = None
            out['region'] = region
            if logger.root.level == logger.DEBUG:
                timestamp = datetime.datetime.now().isoformat()
                file_name = f"data/instances-{region}-{timestamp}.json"
                write_json_file(file_name, out)
            logger.debug(out)
            return out
    except ValueError as err:
        logger.error(f"Obtaining instance list failed. Error : {err}. Skipping!")


def get_instance_ini_conf(access_token, region, instance_id, owner_map):
    url = f"https://{region}.iaas.cloud.ibm.com/v1/instances/{instance_id}/" \
          f"initialization?version=2022-10-18&generation=2"
    headers = {'Authorization': access_token}
    out = curl_execution('get', url, headers, None)
    logger.debug(f"cURL output for getting instance initialization configuration: {out}")
    try:
        if 'keys' in out:
            for key in out['keys']:
                logger.debug(f"SSH Key found in instance {instance_id} init conf. Key Name is {key['name']}.")
                if owner_map:
                    return get_instance_owner(key['name'], owner_map)
                return key['name'], 'NA'
    except TypeError:
        logger.error("Unable to find keys from instance initialization configuration. Skipping!")
    except ValueError as err:
        logger.error(f"Obtaining instance initialization configuration failed. Error : {err}. Skipping!")
    return


def get_instance_owner(key_name, owner_map):
    for key, value in owner_map.items():
        if key_name.startswith(key):
            return key_name, value
    return key_name, 'Unknown'
