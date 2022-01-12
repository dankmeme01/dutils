from urllib.parse import quote_plus
from .errors import *
import requests
import json

class BaseClient:
    def __init__(self, token: str, base: str):
        self.base = base
        self.session = requests.Session()
        self.session.headers["authorization"] = f'Bearer {token}'
        self.session.headers["Accept"] = 'application/json'

    def close(self):
        if self.session is not None:
            self.session.close()
            self.session = None

    def _get(self, endpoint: str):
        if not endpoint.startswith(self.base):
            if not endpoint.startswith("/"):
                endpoint = "/" + endpoint
            endpoint = self.base + endpoint

        endpoint = quote_plus(endpoint, safe='/:')

        r = self.session.get(endpoint)

        match r.status_code:
            case 200:
                return r.json()
            case 403:
                jdump = json.loads(r.content.decode('utf-8'))
                if jdump["reason"] == "accessDenied.invalidIp":
                    raise BAInvalidIP(jdump["message"].partition("from IP ")[2])
                raise BAForbidden("Status code 403: Forbidden. Content: " + r.content.decode('utf-8'))
            case 404:
                raise BANotFound("Status code 404: Not found. Content: " + r.content.decode('utf-8'))
            case ns:
                raise BAUnknown(f"Status code {ns}. Content: " + r.content.decode('utf-8'))