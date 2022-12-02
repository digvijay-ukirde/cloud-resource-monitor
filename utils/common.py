import json
import logging
import requests

logger = logging
logger.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',  level=logging.INFO)


def set_debug_mode():
    logger.getLogger().setLevel(logger.DEBUG)
    return


def read_json_file(file_path):
    json_details = None
    try:
        with open(file_path, 'r') as json_file:
            json_details = json.load(json_file)
            logger.debug(json_details)
    except ValueError as err:
        logger.error(f"Failed while reading json file. Error: {err}")
    return json_details


def write_json_file(file_name, json_data):
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
    except OSError as err:
        logger.error(f"Failed while writing json file. Error: {err}")
    return


def write_elk_file(file_name, data):
    try:
        with open(file_name, 'a') as f:
            json.dump(data, f)
            f.write("\n")
    except OSError as err:
        logger.error(f"Failed while appending file. Error: {err}")
    return


def curl_execution(action, url, headers, data):
    try:
        if action == 'put':
            res = requests.put(url, headers=headers, data=data)
        elif action == 'post':
            res = requests.post(url, headers=headers, data=data)
        elif action == 'get':
            res = requests.get(url, headers=headers, data=data)
        elif action == 'patch':
            res = requests.patch(url, headers=headers, data=data)
        else:
            logger.info("Requested cURL command action is not available.")
    except requests.exceptions.Timeout as err:
        logger.error("Requested cURL command got timeout.", err)
    except requests.exceptions.TooManyRedirects as err:
        logger.error("Requested cURL command got to many redirects.", err)
    except requests.exceptions.RequestException as err:
        logger.error("Requested cURL command got request exception.", err)
    except Exception as err:
        print("While executing cURL command. Execution halted!", err)
    if res.ok:
        return res.json()
    else:
        return None
