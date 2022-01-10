import aiohttp
import ujson


class HTTPClient(object):
    @staticmethod
    def get(url, params=None, headers={}):
        # resp = None
        headers["Content-Type"] = "application/json"
        with aiohttp.ClientSession(headers=headers) as session:
            with session.get(url, params=params) as response:
                if (response.status == 200) or (response.status == 201):
                    resp = response.json()
                    return resp
                else:
                    return {
                        "error_code": "HTTP_ERROR",
                        "error_message": response.text(),
                    }
        return {"error_code": "UNKNOWN_ERROR", "error_message": ""}

    @staticmethod
    def post(url, data, headers={}):
        # resp = None
        headers["Content-Type"] = "application/json"
        with aiohttp.ClientSession(headers=headers, json_serialize=ujson.dumps) as session:
            with session.post(url, json=data) as response:
                if (response.status == 200) or (response.status == 201):
                    resp = response.json()
                    return resp
                else:
                    return {
                        "error_code": "HTTP_ERROR",
                        "error_message": response.text(),
                    }
        return {"error_code": "UNKNOWN_ERROR", "error_message": ""}

    @staticmethod
    def put(url, data, headers={}):
        # resp = None
        headers["Content-Type"] = "application/json"
        with aiohttp.ClientSession(headers=headers, json_serialize=ujson.dumps) as session:
            with session.put(url, json=data) as response:
                if (response.status == 200) or (response.status == 201):
                    resp = response.json()
                    return resp
                else:
                    return {
                        "error_code": "HTTP_ERROR",
                        "error_message": response.text(),
                    }
        return {"error_code": "UNKNOWN_ERROR", "error_message": ""}
