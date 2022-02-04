import json

import requests
from requests.models import Response


class HttpClient:
    def get(self, url, params=None, headers=None):
        r = requests.get(url=url, params=params, headers=headers)
        return self._parse_response(r)

    def post(self, url, params=None, body=None, headers=None):
        if not body or not isinstance(body, dict):
            raise Exception("Body type must be dict")
        r: Response = requests.post(url=url, json=body, params=params, headers=headers)
        if r.status_code not in [200, 201, 204]:
            return {"code": r.status_code, "error": json.loads(r.content)}
        return self._parse_response(r)

    def _parse_response(self, r: Response):
        if r.status_code == 200 or r.status_code == 201:
            return json.loads(r.content)
        else:
            return None


client = HttpClient()
