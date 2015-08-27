#coding=UTF-8
import requests
import xmltodict
import json
import io

BASE_URL = "http://opendata.cwb.gov.tw/opendataapi"
payload = {"dataid": "F-C0032-001", "authorizationkey": ""}

resp = requests.get(BASE_URL, params=payload)
respJson = json.dumps(xmltodict.parse(resp.text), indent=4, ensure_ascii=False)
file = io.open("cwbJson.txt", "w", encoding="utf-8")
file.write(respJson)
file.close()