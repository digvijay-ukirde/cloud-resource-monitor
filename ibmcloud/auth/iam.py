from utils.common import logger
from utils import common


def get_access_token(api_key):
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
    data = {'grant_type': 'urn:ibm:params:oauth:grant-type:apikey', 'apikey': api_key}
    out = common.curl_execution('post', url, headers, data)
    try:
        if 'access_token' in out:
            logger.debug(f"Access Token: {out['access_token']}")
            return out['access_token']
    except TypeError as err:
        logger.error(f"No access token entry found. Obtaining IAM access token failed. Error: {err}. Exiting!!")
    except ValueError as err:
        logger.error(f"Obtaining IAM access token failed. Error: {err}. Exiting!")
        exit(1)
