# Libraries to import
import requests
import urllib3
import json
import datetime
import logging
import time

# Variable initialization
deviceInputData = {
    "isAvailable": False,
    "state": "",
    "timestamp": "",
    "metrics": []
}


class REST:
    # Creating HTTP session for the API connection
    def __init__(self):
        self.session = requests.Session()

    # Building the dictionary
    def buildDictionary(self):
        # Defining vars
        varNameList = []
        varTypeList = []
        # Defining globals
        global deviceInputData
        # Adding to log current state
        logging.info('API State: Data dictionary updated started')
        deviceInputData['state'] = 'API State: Data dictionary updated started'
        # Requesting the dictionary
        payload = self.session.request('GET', 'https://localhost/ehmi/data.dictionary.json', verify=False)
        # Checking to make sure response is OK
        if payload.status_code == 200:
            deviceInputData['isAvailable'] = True
            deviceInputData['state'] = 'API State: Updating data dictionary...'
            # Data pre-processing
            dictionary = json.loads(payload.content)
            for key in dictionary['HmiVariables2']:
                varNameList.append(key[13:])
                varTypeList.append(dictionary['HmiVariables2'][key]['Type'])
        elif payload.status_code == 404:
            logging.info('API State: Unavailable')
            deviceInputData['isAvailable'] = False
            deviceInputData[
                'state'] = 'API State: Unavailable (did you download a PLCnext project with an HMI component yet?)'
        else:
            logging.info('API State: Unavailable')
            deviceInputData['isAvailable'] = False
            deviceInputData['state'] = 'API State: Unknown Error'

        return varNameList, varTypeList

    # Reading tags from the API
    def readAPI(self, varNameList, varTypeList):
        # Defining vars
        index = 0
        varObj = {}
        varList = []
        # Defining globals
        global deviceInputData
        # Building URL and headers
        URL = 'https://localhost/_pxc_api/api/variables/?pathPrefix=Arp.Plc.Eclr/&paths=' + readString(varNameList)
        # API Request
        payload = self.session.request('GET', URL, verify=False)
        # Checking to make sure response is OK
        if payload.status_code == 200:
            logging.info("API State: New API data received")
            deviceInputData['isAvailable'] = True
            deviceInputData['state'] = 'API State: New API data received'
            deviceInputData['timestamp'] = str(datetime.datetime.now())
            # Data pre-processing
            variables = json.loads(payload.content)
            for var in variables['variables']:
                varObj.clear()
                varObj['name'] = var['path'][13:]
                varObj['value'] = var['value']
                varObj['type'] = varTypeList[index]
                varList.append(varObj.copy())
                index = index+1
            deviceInputData['metrics'] = varList
        elif payload.status_code == 404:
            logging.info('API State: Unavailable')
            deviceInputData['isAvailable'] = False
            deviceInputData[
                'state'] = 'API State: Unavailable (did you download a PLCnext project with an HMI component yet?)'
        else:
            logging.info('API State: Unavailable')
            deviceInputData['isAvailable'] = False
            deviceInputData['state'] = 'API State: Unknown Error'
        return deviceInputData


def readString(varNameList):
    # Defining tags
    readStr = ''
    # Creating the readString
    for varName in varNameList:
        readStr = readStr + varName + ','
    readStr = readStr[:-1]
    return readStr


def getData(waitTime):
    time.sleep(waitTime)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    api = REST()
    tagNames, tagTypes = api.buildDictionary()
    variables = api.readAPI(tagNames, tagTypes)
    return variables
