import datetime
from utils.common import logger
from utils.common import curl_execution
from utils.common import write_json_file


def get_bare_metal_server_list(access_token, region):
    url = f"https://{region}.iaas.cloud.ibm.com/v1/bare_metal_servers?limit=100&version=2022-10-18&generation=2"
    headers = {'Authorization': access_token}
    out = curl_execution('get', url, headers, None)
    logger.debug(f"cURL output for listing bare metal servers: {out}")
    try:
        if 'bare_metal_servers' in out:
            if 'next' in out:
                while out['next']:
                    url = f"{out['next']['href']}&version=2022-10-18&generation=2"
                    logger.debug(f"Updated URL: {url}")
                    next_out = curl_execution('get', url, headers, None)
                    logger.debug(f"cURL output for new bare metal servers: {next_out}")
                    if 'bare_metal_servers' in next_out:
                        for bare_metal_server in next_out['bare_metal_servers']:
                            out['bare_metal_servers'].append(bare_metal_server)
                        if 'next' in next_out:
                            out['next'] = next_out['next']
                        else:
                            out['next'] = None
            out['region'] = region
            if logger.root.level == logger.DEBUG:
                timestamp = datetime.datetime.now().isoformat()
                file_name = f"data/bare_metal_servers-{region}-{timestamp}.json"
                write_json_file(file_name, out)
            logger.debug(out)
            return out
    except ValueError as err:
        logger.error(f"Obtaining bare metal server list failed. Error : {err}. Skipping!")


def get_bare_metal_server_ini_conf(access_token, region, bare_metal_server_id, owner_map):
    url = f"https://{region}.iaas.cloud.ibm.com/v1/bare_metal_servers/{bare_metal_server_id}/" \
          f"initialization?version=2022-10-18&generation=2"
    headers = {'Authorization': access_token}
    out = curl_execution('get', url, headers, None)
    logger.debug(f"cURL output for getting bare metal server initialization configuration: {out}")
    try:
        if 'keys' in out:
            for key in out['keys']:
                logger.debug(f"SSH Key found in bare metal server {bare_metal_server_id} init conf. "
                             f"Key Name is {key['name']}.")
                if owner_map:
                    return get_bare_metal_server_owner(key['name'], owner_map)
                return key['name'], 'NA'
    except TypeError:
        logger.error("Unable to find keys from bare metal server initialization configuration. Skipping!")
    except ValueError as err:
        logger.error(f"Obtaining bare metal server initialization configuration failed. Error : {err}. Skipping!")
    return


def get_bare_metal_server_owner(key_name, owner_map):
    for item in owner_map:
        for key in item['keys']:
            if key_name.startswith(key):
                return key_name, item['id'], item['name']
    return key_name, 'Unknown', 'Unknown'
