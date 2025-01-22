import json
import os

import requests
import yaml

from poja_service import get_file_content_from, write_temp_file, write_cli_version_in_conf_file

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


def get_sam_object(event):
    conf = yaml.safe_load(get_file_content_from(event, "conf"))
    public_version = conf["general"]["public_generator_version"]
    print("CLI Version :" + public_version)
    sam = [sam for sam in sam_apps if sam.get("public_version") == public_version][0]
    return sam


def gen(event):
    sam = get_sam_object(event)
    content = get_file_content_from(event, "conf")
    conf_file = write_temp_file(write_cli_version_in_conf_file(content, sam["cli_version"]), "yml")
    return send_request_to_sam_app(sam["url"], conf_file)


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
