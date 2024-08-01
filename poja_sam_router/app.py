import json
import os

import requests
import yaml

from poja_service import get_file_content_from, write_temp_file

POJA_SAM_API_KEY = os.getenv("POJA_SAM_API_KEY")

sam_apps = json.load(open("sam-versions.json"))


def lambda_handler(event, context):
    try:
        code_uri = gen(event)
    except Exception as e:
        return {"code": "500", "message": e}
    else:
        return code_uri


def gen(event):
    sam_url = get_sam_url(event)
    conf_file = write_temp_file(get_file_content_from(event, "conf"), "yml")
    return send_request_to_sam_app(sam_url, conf_file)


def get_sam_url(event):
    conf = yaml.safe_load(get_file_content_from(event, "conf"))
    cli_version = conf["general"]["cli_version"]
    sam = [sam for sam in sam_apps if sam["cli_version"] == cli_version][0]
    return sam["url"]


def send_request_to_sam_app(sam_url, file):
    with open(file, "rb") as conf_file:
        files = {"conf": conf_file}
        headers = {"x-api-key": POJA_SAM_API_KEY}

        response = requests.put(sam_url, files=files, headers=headers)

    return response.json()
