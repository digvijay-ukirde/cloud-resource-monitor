from utils.common import logger, read_json_file
from elasticsearch import Elasticsearch
import glob
import requests
requests.packages.urllib3.disable_warnings()


def check_connection(file_path):
    elastic_data = read_json_file(file_path)
    elastic = None
    try:
        if 'host' in elastic_data and 'port' in elastic_data and 'user' in elastic_data and 'secrete' in elastic_data:
            elastic = Elasticsearch(f"https://{elastic_data['host']}:{elastic_data['port']}",
                                    http_auth=(elastic_data['user'], elastic_data['secrete']), verify_certs=False)
        else:
            elastic = Elasticsearch(f"http://localhost:9200")
    except ConnectionError as err:
        logger.error(f"Connection to Elastic host failed. Error: {err}. "
                     f"Uploading resource data to ElasticSearch host failed. Exiting!")
        exit(1)
    return elastic


def delete_older_data(elastic, data):
    if elastic.indices.exists(index='resources'):
        body = {'query': {'match': {'account.keyword': data['account']}}}
        out = elastic.delete_by_query(index='resources', body=body)
        logger.debug(f"ElasticSearch Delete query response: {out}")


def upload_data(elastic, data):
    out = elastic.index(index='resources', body=data)
    logger.debug(f"ElasticSearch creating document query response: {out}")
    return


def upload_file(elastic, path):
    for file in glob.glob(f"{path}/*.json"):
        data = read_json_file(file)
        upload_data(elastic, data)
    return
