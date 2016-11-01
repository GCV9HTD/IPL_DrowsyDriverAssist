import glob
import base64
import requests
import os
import sys
from SOAPpy import SOAPProxy
import suds
import subprocess
import time

url="http://drowsyservice.azurewebsites.net/DrowsyService.svc?wsdl"
headers = {'content-type': 'application/soap+xml'}
path ='/home/pi/drowsyImages/*.jpg'
namespace = "http://tempuri.org/"
server = SOAPProxy(url,namespace)
client = suds.client.Client(url)


count = 0


files = glob.glob(path)
for name in files:
    try:
        encoded_string = ""
        with open(name, "rb") as f:
            encoded_string = base64.b64encode(f.read())
             #b = bytearray(f.read())
             #print b
            
        print name.split("/")[4].replace('.jpg','')
        subprocess.call(["curl", "-X", "POST", "-H", "Content-Type: text/xml", "-H", "SOAPAction: \"http://tempuri.org/IDrowsyService/StoreDrowsyDetails\"",
             "-d", """<?xml version="1.0" encoding="UTF-8"?>
                    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/" xmlns:drow="http://schemas.datacontract.org/2004/07/DrowsyMonitorService">
                       <soapenv:Header/>
                       <soapenv:Body>
                          <tem:StoreDrowsyDetails>
                          <tem:data>
                               <drow:AlertImage>"""+encoded_string+"""</drow:AlertImage>        
                           </tem:data>
                          </tem:StoreDrowsyDetails>
                       </soapenv:Body>
                    </soapenv:Envelope>""" , "http://drowsyservice.azurewebsites.net/DrowsyService.svc"])

        print "Data sent to Webservice successfully"
        os.rename (name, name+"Proc");
    except Exception as exc:
        print 'Unsuccessful', exc

