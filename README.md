# About
This unofficial script looks URLs up in Zscaler Site Review portal, whether they are malicious or not.

Note that Zscaler Site Review is available for Zscaler customers only and has to be accessed via Zscaler cloud.
Furthermore, no Zscaler Site Review APIs are publicly documented, so the code is based on call observation via
web browser only.

This unofficial script is provided AS-IS, use it at your own risk.

## Setup the environment

To avoid conflicts between different modules we'll use Python virtual environment:

```shell
$ cd ip_lookup
$ chmod +x resolve.py      # enable running without explicit python cmd
$ python -m venv venv
$ source venv/bin/activate
(venv) $
```

After venv is set up, you'll need to install the requirements.

```shell
(venv) $ pip install --upgrade pip
(venv) $ pip install -r requirements.txt
```

# Usage
URL cache timeout is set to 14 days by default.

## Python venv

Enable virtual environment scope:
```shell
$ source venv/bin/activate
(venv) $ 
```

Different scripts could be run in different windows and thus in different venv, however, 
venv can be disabled as well:
```shell
(venv) $ deactivate
$ 
```

## Certificate error
API call might fail due to Zscaler certificate being untrusted by OpenSSL backend:
```shell
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1006)
```

 In such a case you could specify the certificate to trust directly for the duration of the session 
 (can be obtained from Site Review via web browser):
```shell
$ (venv) export SSL_CERT_FILE="`pwd`/sitereview-zscaler-com-chain.pem"
```

If needed, certificate can be appended to the OS trusted certificate store. Use the following
to figure out the exact location and append the certificate:
```shell
$ (venv) python3 -c "import ssl; print(ssl.get_default_verify_paths())"
$ (venv) cat sitereview-zscaler-com-chain.pem >> /usr/lib/ssl/cacert.pem
$ (venv) pip install pip_system_certs
```

If the error persists, append Site Review certificate to certifi trusted store file as well:
```shell
$ (venv) python3 -m certifi
/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/certifi/cacert.pem

$ (venv) cat sitereview-zscaler-com-chain.pem >> /Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/certifi/cacert.pem
```

## JSON parsing error
Site Review has to be accessed through ZIA, otherwise the following exception is raised due to HTTP 403 response:
```shell
04/11/2024 22:46:15 [resolve:81] [INFO] Resolving URLs from text file list.txt
  File "lookup.py", line 108, in lookup_urls
    lookup = self._lookup_batch(batch)
             ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "lookup.py", line 133, in _lookup_batch
    response_json = json.loads(response.text)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/decoder.py", line 337, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/decoder.py", line 355, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

## Options

By default, the tool searches for the latest relevant file, if a corresponding parameter is provided
without value.

```shell
(venv) $ ./resolve.py --help
usage: resolve.py [-h] [--har [FILE]] [-l [FILE]] [-c FILE] [-x [FILE]] [--excel-export [FILE]] [--json-export [FILE]]

Lookup URLs with Zscaler Site Review and mark threats

options:
  -h, --help            show this help message and exit
  -l [FILE], --list [FILE]
                        filename for the list of URLs; latest .txt used by default
  -c FILE, --cache FILE
                        cache filename; 'zurl_cache.json' is used by default
  -x [FILE], --excel [FILE]
                        CSE SSL spreadsheet filename; latest .xlsx is used by default
  --excel-export [FILE]
                        Export data to Excel
  --json-export [FILE]  Export data to JSON
```

### Running lookup for IP list in text file and JSON output
```shell
(venv) $  ./resolve.py -l --json-export
04/11/2024 22:46:15 [resolve:81] [INFO] Resolving URLs from text file list.txt
04/11/2024 22:46:28 [lookup:103] [INFO] cache_hits=0 | lookups=791
04/11/2024 22:46:28 [resolve:86] [INFO] Saving URLs from text file to JSON out.json
04/11/2024 22:46:28 [resolve:100] [INFO] Script ran for 0:00:12.639313 seconds.
```

### Running lookup for IP list in text file and Excel output
```shell
(venv) $  ./resolve.py -l --excel-export
04/11/2024 22:45:30 [resolve:81] [INFO] Resolving URLs from text file list.txt
04/11/2024 22:45:42 [lookup:103] [INFO] cache_hits=0 | lookups=791
04/11/2024 22:45:42 [resolve:92] [INFO] Saving URLs from text file to Excel out.xlsx
04/11/2024 22:45:42 [resolve:100] [INFO] Script ran for 0:00:12.318244 seconds.
```

### Running lookup for CSE SSL spreadsheet
Changes are saved inline in the spreadsheet provided.

```shell
(venv) $  ./resolve.py -x
04/11/2024 22:47:16 [resolve:96] [INFO] Resolving URLs from CSE SSL spreadsheet in_src.xlsx
04/11/2024 22:47:19 [lookup:103] [INFO] cache_hits=5 | lookups=188
04/11/2024 22:47:20 [resolve:100] [INFO] Script ran for 0:00:03.407312 seconds.
```