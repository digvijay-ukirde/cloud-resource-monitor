import datetime
from utils.common import logger
from utils.common import curl_execution
from utils.common import write_json_file


def get_image_list(access_token, region):
    url = f"https://{region}.iaas.cloud.ibm.com/v1/images?limit=100&version=2022-10-18&generation=2"
    headers = {'Authorization': access_token}
    out = curl_execution('get', url, headers, None)
    logger.debug(f"cURL output for listing images: {out}")
    try:
        if 'images' in out:
            if 'next' in out:
                while out['next']:
                    url = f"{out['next']['href']}&version=2022-10-18&generation=2"
                    logger.debug(f"Updated URL: {url}")
                    next_out = curl_execution('get', url, headers, None)
                    logger.debug(f"cURL output for new images: {next_out}")
                    if 'images' in next_out:
                        for images in next_out['images']:
                            out['images'].append(images)
                        if 'next' in next_out:
                            out['next'] = next_out['next']
                        else:
                            out['next'] = None
            out['region'] = region
            if logger.root.level == logger.DEBUG:
                timestamp = datetime.datetime.now().isoformat()
                file_name = f"data/images-{region}-{timestamp}.json"
                write_json_file(file_name, out)
            logger.debug(out)
            return out
    except TypeError as err:
        logger.error(f"Obtaining image list failed. Error : {err}. Skipping!")
