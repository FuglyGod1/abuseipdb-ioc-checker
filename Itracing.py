import requests
import datetime #so it generates a unique name for the file each time when executed
import csv
import os #we will use this to hide the api key 

#step 1 read and load the ips
def load_ips(filename):
    file = open(filename, 'r')
    f = file.readlines()
    ipList = []
    for line in f:
        ipList.append(line.strip())

    file.close()
    return ipList

#step 2 check the list of ips and store it in results for future use
def check_ips(ipList, apiKey):
    url = 'https://api.abuseipdb.com/api/v2/check'
    results = []

    for ip in ipList:
        querystring = {
            'ipAddress': ip
        }

        headers = {
            'Accept': 'application/json',
            'Key': apiKey
        }
        response = requests.request(method='GET', 
                                    url=url, 
                                    headers=headers, 
                                    params=querystring)
        data = response.json()['data']

        #make dictionary to access the dictionary and store it 
        result = {
            'ip' : data['ipAddress'],
            'abuseConfidenceScore' : data['abuseConfidenceScore'],
            'countryCode': data['countryCode']
        }

        results.append(result)
    return results

#step 3 sort the ips
def sort_results(results):
    results.sort(key=lambda x: (x['abuseConfidenceScore'], x['countryCode']))

#step 4 create new filename with a unique each time when the program runs
def save(results):
    time = datetime.datetime.now()
    filename = time.strftime("results_%Y%m%d_%H%M%S.txt") #we cant have : as filenames since it is part of the time, format it by year, month, date, hour,minute, second
    file = open(filename, 'w')
    for result in results:
        file.write(str(result) + '\n')
    file.close()

#step 5 read the csv document, compare it with our ips
def load_ioc(filename):
    iocList = []
    file = open(filename, 'r')
    reader = csv.DictReader(file) #map each row into a dictionary, ignores first row
    for row in reader:
        iocList.append(row)
    file.close()
    return iocList

def print_valid_ips(results, iocList):
    for result in results: #for each result check for every iocList
        found = False #so it does not keep repeatedly printing
        for row in iocList:
            if row['ip'] == result['ip']:
                found = True
                if row['rule'] == 'allow':
                    print(
                        "ip: " + result['ip'],
                        ", score: " + str(result['abuseConfidenceScore']),
                        ", country: " + result['countryCode'],
                        ", ioc description: " + row['description'],
                        ", rule name: " + row['rule']
                    )

        if found == False: #tracks whether the IP exists in the IOC list
            if result['abuseConfidenceScore'] <= 25:
                print(
                        "ip: " + result['ip'],
                        ", score: " + str(result['abuseConfidenceScore']),
                        ", country: " + result['countryCode']
                    )
\

def main():
    #remember to set the api key in the terminal , do $env:ABUSE_API_KEY="the api key"
    apiKey = os.getenv("ABUSE_API_KEY") 
    if apiKey is None:
        print("API key not found")
        exit()
    ipList = load_ips('abuse_db.txt')
    results = check_ips(ipList, apiKey)
    sort_results(results)
    save(results)

    iocList = load_ioc('ioc.csv')
    print_valid_ips(results, iocList)

main()

