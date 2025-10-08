import json

import requests
import shutil
from ratelimit import limits, sleep_and_retry

CALLS = 1
PERIOD = 1.5  # seconds

def download(url, path, **kwargs):
    kwargs['stream'] = True
    r = requests.get(url, **kwargs)
    if r.status_code == 200:
        with open(path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

@sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
def http_ratelimited(method, url, **kwargs):
    return method(url, **kwargs)


def pretty_print_json(data):
    if data:
        print(json.dumps(data, indent=4, sort_keys=True))
    else:
        print("Nessun dato da visualizzare.")


def print_all_headers(headers):
    print("\n--- Headers ---")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    print("--------------------------------------")

def get_without_redirect(url, **kwargs):
    kwargs['allow_redirects'] = False
    return requests.get(url, **kwargs)