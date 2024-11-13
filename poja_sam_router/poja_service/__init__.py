import base64
import tempfile

import yaml
from requests_toolbelt.multipart import decoder


def get_file_content_from(event, key):
    if event["isBase64Encoded"]:
        body = base64.b64decode(event["body"])
    else:
        body = event["body"].encode("utf-8")

    content_type = event["headers"]["content-type"]
    multipart_data = decoder.MultipartDecoder(body, content_type)

    content = ""
    for part in multipart_data.parts:
        content_disposition = part.headers[b"Content-Disposition"].decode("utf-8")

        if "filename" and f"{key}" in content_disposition:
            content = part.text

    return content


def write_temp_file(content, suffix):
    with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=f".{suffix}"
    ) as file:
        file.write(content)
        file.flush()
    return file.name


def write_cli_version_in_conf_file(content, cli_version):
    content_as_yml = yaml.safe_load(content)
    content_as_yml["general"]["cli_version"] = cli_version
    return yaml.safe_dump(content_as_yml)
