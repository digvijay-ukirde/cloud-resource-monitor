import datetime
from utils.common import logger
from utils.common import curl_execution
from utils.common import write_json_file


def get_dedicated_host_list(access_token, region):
    url = f"https://{region}.iaas.cloud.ibm.com/v1/dedicated_hosts?limit=100&version=2022-10-18&generation=2"
    headers = {'Authorization': access_token}
    out = curl_execution('get', url, headers, None)
    logger.debug(f"cURL output for listing dedicated hosts: {out}")
    try:
        if 'dedicated_hosts' in out:
            if 'next' in out:
                while out['next']:
                    url = f"{out['next']['href']}&version=2022-10-18&generation=2"
                    logger.debug(f"Updated URL: {url}")
                    next_out = curl_execution('get', url, headers, None)
                    logger.debug(f"cURL output for new dedicated hosts: {next_out}")
                    if 'dedicated_hosts' in next_out:
                        for dedicated_host in next_out['dedicated_hosts']:
                            out['dedicated_hosts'].append(dedicated_host)
                        if 'next' in next_out:
                            out['next'] = next_out['next']
                        else:
                            out['next'] = None
            out['region'] = region
            if logger.root.level == logger.DEBUG:
                timestamp = datetime.datetime.now().isoformat()
                file_name = f"data/dedicated_hosts-{region}-{timestamp}.json"
                write_json_file(file_name, out)
            logger.debug(out)
            return out
    except ValueError as err:
        logger.error(f"Obtaining dedicated hosts list failed. Error : {err}. Skipping!")
