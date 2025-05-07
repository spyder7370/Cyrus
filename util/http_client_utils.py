import json
from urllib.request import Request, urlopen

from util.dict_utils import DictUtils
from util.logger import log
from util.string_utils import StringUtils


def make_get_request(url: str, headers: dict[str, str]):
    try:
        if StringUtils.is_empty(url):
            return {}

        req = Request(url)

        if DictUtils.is_not_empty(headers):
            for header in headers:
                req.add_header(header, headers[header])

        response_string = urlopen(req).read().decode("utf-8")
        return json.loads(response_string)
    except Exception as e:
        log.error(
            "Exception encountered while making get request to: %s: %s",
            url,
            str(e),
            exc_info=e,
        )
        return {}
