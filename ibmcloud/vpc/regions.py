from utils.common import logger
from utils.common import read_json_file


def get_endpoint_map(resource_type):
    file_path = f"ibmcloud/vpc/vpc_static_config.json"
    json_details = read_json_file(file_path)
    logger.debug(f"VPC region map: {json_details}")
    return json_details[resource_type]

