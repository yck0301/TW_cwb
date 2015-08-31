#coding=UTF-8
import requests
import xmltodict
import json
import io
import datetime
import dateutil.parser
import pytz

def dlCwb36hrForecast(authorizationkey):
	"""Get 36 hr forecast data from CWB open data interface.
	
	Args:
		authorizationkey: from registration
	
	Returns:
		xml type string
	"""
	
	BASE_URL = "http://opendata.cwb.gov.tw/opendataapi"
	payload = {"dataid": "F-C0032-001", "authorizationkey": authorizationkey}
	return requests.get(BASE_URL, params=payload)
	
def convertObjToJsonFile(obj, destFile):
	"""Convert object to JSON, then write to file.
	
	Args:
		obj: collection object.
		
		destFile: the file path.
	"""
	
	respJson = json.dumps(obj, indent=4, ensure_ascii=False)
	file = io.open(destFile, "w", encoding="utf-8")
	file.write(respJson)
	file.close()
	
def findSuitableItem(data):
	"""Find the closest data that compares with current time.
	
	Args:
		data: XML type string.

	Returns:
		refined: dict object.
		example:
		{
			"list": [{
				"tempHigh": "28", 
				"tempLow": "27", 
				"name": "臺北市", 
				"brief": "陰時多雲短暫陣雨或雷雨"
			},...]
			"result": {
				"msg": "success", 
				"code": 0
			}
		}
	"""
	
	items = xmltodict.parse(data.text)["cwbopendata"]["dataset"]["location"]
	refined = {"list": [], "result": {"code": 1, "msg": ""}}
	FIELD_MAP = {"Wx": "brief", "MaxT": "tempHigh", "MinT": "tempLow"}
	
	taipeiTimezone = pytz.timezone("Asia/Taipei")
	localtime =  taipeiTimezone.localize(datetime.datetime.now())
	
	for item in items:
		weather = {"name": item["locationName"]}
		elements = item["weatherElement"]
		for element in elements:
			elementName = element["elementName"]
			if elementName in ["Wx","MaxT", "MinT"]:
				for timeslot in element["time"]:
					startTime = dateutil.parser.parse(timeslot["startTime"])
					endTime = dateutil.parser.parse(timeslot["endTime"])
					if localtime >= startTime and localtime < endTime:
						weather[FIELD_MAP[elementName]] = timeslot["parameter"]["parameterName"]
						break
		
		
		if "brief" in weather and "tempHigh" in weather and "tempLow" in weather:
			#print weather["name"] + ":" + weather["brief"] + "/" + weather["tempHigh"] + "-" + weather["tempLow"]
			refined["list"].append(weather)
			
	if len(refined["list"]) > 0:
		refined["result"]["code"] = 0
		refined["result"]["msg"] = "success"
			
	return refined

if __name__ == "__main__":
	# Download from CWB
	AUTHORIZATION_KEY = ""
	DEST_FILE = "cwbJson.txt"
	resp = dlCwb36hrForecast(AUTHORIZATION_KEY)
	convertObjToJsonFile(findSuitableItem(resp), DEST_FILE)
