import json
import os

import requests
import yaml

from poja_service import get_file_content_from, write_temp_file

API_KEY = os.getenv("POJA_SAM_API_KEY")

sam_apps = json.load(open("sam-versions.json"))


def lambda_handler(event, context):
    if not is_api_key_valid(event):
        return {"code": "403", "message": "Unauthorized"}
    else:
        try:
            code_uri = gen(event)
        except Exception as e:
            return {"code": "500", "message": str(e)}
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


def is_api_key_valid(event):
    if "x-api-key" not in event["headers"]:
        return False
    else:
        api_key = event["headers"]["x-api-key"]
        return api_key == API_KEY


def send_request_to_sam_app(sam_url, file):
    with open(file, "rb") as conf_file:
        files = {"conf": conf_file}
        headers = {"x-api-key": API_KEY}

        response = requests.put(sam_url, files=files, headers=headers)

    return response.json()
