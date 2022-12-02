import datetime
from utils.common import logger
from utils.common import curl_execution
from utils.common import write_json_file


def get_floating_ip_list(access_token, region):
    url = f"https://{region}.iaas.cloud.ibm.com/v1/floating_ips?limit=100&version=2022-10-18&generation=2"
    headers = {'Authorization': access_token}
    out = curl_execution('get', url, headers, None)
    logger.debug(f"cURL output for listing floating IP: {out}")
    try:
        if 'floating_ips' in out:
            if 'next' in out:
                while out['next']:
                    url = f"{out['next']['href']}&version=2022-10-18&generation=2"
                    logger.debug(f"Updated URL: {url}")
                    next_out = curl_execution('get', url, headers, None)
                    logger.debug(f"cURL output for new floating IPs: {next_out}")
                    if 'floating_ips' in next_out:
                        for floating_ip in next_out['floating_ips']:
                            out['floating_ips'].append(floating_ip)
                        if 'next' in next_out:
                            out['next'] = next_out['next']
                        else:
                            out['next'] = None
            out['region'] = region
            timestamp = datetime.datetime.now().isoformat()
            if logger.root.level == logger.DEBUG:
                file_name = f"data/floating_ips-{region}-{timestamp}.json"
                write_json_file(file_name, out)
            logger.debug(out)
            return out
    except TypeError:
        logger.error(f"Unable to find floating IP list. Skipping!")
    except ValueError as err:
        logger.error(f"Obtaining floating IP list failed. Error : {err}. Skipping!")
