import datetime
from utils.common import logger
from utils.common import curl_execution
from utils.common import write_json_file


def get_workspace_list(access_token, region):
    url = f"https://{region}.schematics.cloud.ibm.com/v1/workspaces?limit=2000"
    headers = {'Authorization': access_token}
    out = curl_execution('get', url, headers, None)
    logger.debug(f"cURL output for listing workspaces: {out}")
    try:
        if 'workspaces' in out:
            if 'next' in out:
                while out['next']:
                    url = out['next']['href']
                    logger.debug(f"Updated URL: {url}")
                    next_out = curl_execution('get', url, headers, None)
                    logger.debug(f"cURL output for new workspaces: {next_out}")
                    if 'workspaces' in next_out:
                        for workspaces in next_out['workspaces']:
                            out['workspaces'].append(workspaces)
                        if 'next' in next_out:
                            out['next'] = next_out['next']
                        else:
                            out['next'] = None
            out['region'] = region
            if logger.root.level == logger.DEBUG:
                timestamp = datetime.datetime.now().isoformat()
                file_name = f"data/workspaces-{region}-{timestamp}.json"
                write_json_file(file_name, out)
            logger.debug(out)
            return out
    except ValueError as err:
        logger.error(f"Obtaining workspaces list failed. Error : {err}. Skipping!")
    except TypeError as err:
        logger.warning(f"Obtaining workspaces list failed. Type Error : {err}. Skipping!")
    return


def get_resource_list(access_token, region, workspace_id):
    url = f"https://{region}.schematics.cloud.ibm.com/v1/workspaces/{workspace_id}/resources"
    headers = {'Authorization': access_token}
    out = curl_execution('get', url, headers, None)
    logger.debug(f"cURL output for listing workspace resources: {out}")
    try:
        if 'resources' in out:
            if 'next' in out:
                while out['next']:
                    url = out['next']['href']
                    logger.debug(f"Updated URL: {url}")
                    next_out = curl_execution('get', url, headers, None)
                    logger.debug(f"cURL output for new resources: {next_out}")
                    if 'resources' in next_out:
                        for resources in next_out['resources']:
                            out['resources'].append(resources)
                        if 'next' in next_out:
                            out['next'] = next_out['next']
                        else:
                            out['next'] = None
            out['region'] = region
            if logger.root.level == logger.DEBUG:
                timestamp = datetime.datetime.now().isoformat()
                file_name = f"data/resources-{region}-{timestamp}.json"
                write_json_file(file_name, out)
            logger.debug(out)
            return out
    except ValueError as err:
        logger.error(f"Obtaining resources list failed. Error : {err}. Skipping!")
    except TypeError as err:
        logger.warning(f"Obtaining resources list failed. Type Error : {err}. Skipping!")

    return
