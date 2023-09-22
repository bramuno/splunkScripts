## activate the venv first:  source splunkEnv3.9/bin/activate
## usage: python3 getInsputStatus.py
## matching a search of logs: python3 getInsputStatus.py -b checkpoint
## watching a SPECIFIC log file: python3 getInsputStatus.py -w /path/to/log.txt
## connect to remote host:  python3 getInsputStatus.py -H hostname.com -b checkpoint
## monitor percentage completed of tails including a keyword:  python3 getInsputStatus.py -H hostname.com -s splunkd.log -m 1
## control the refresh delay:  python3 getInsputStatus.py -H hostname.com -d 3
## verbose mode: python3 getInsputStatus.py -H hostname.com -v 1
## ensure the remote host has the correct password set for the username
##
username = ""	
password = ""
############################################
import time, sys, subprocess, pdb, glob, untangle # pip3 install untangle
import json # pip3 install jsonlines
import datetime, re, getopt, argparse, requests, os, json, time, urllib3
from colorama import init as colorama_init  # pip3 install colorama
from colorama import Fore, Style
import xml.etree.ElementTree as ET
urllib3.disable_warnings()
#
parser = argparse.ArgumentParser()
############################################
parser.add_argument("-v", "--verbose", help = "verbose")
parser.add_argument("-H", "--host", help = "target hostname, defaults to localhost")
parser.add_argument("-m", "--monitor", help = "watch with percent status")
parser.add_argument("-s", "--search", help = "keyword search, returns that search")
parser.add_argument("-b", "--batch", help = "return all logs still in batch mode")
parser.add_argument("-w", "--watch", help = "watch a specific log file")
parser.add_argument("-d", "--delay", help = "number of seconds delay between monitor calls")
args = parser.parse_args()
############################################
if args.verbose:
    verbose=int(args.verbose)
    if verbose >= 1:
        print("Diplaying verbose as: % s" % args.verbose)
else:
    verbose=0
if args.search:
    search=str(args.search)
    if verbose >= 1:
        print("Diplaying search as: % s" % args.search)
else:
    search=""
if args.batch:
    batch = 1
    if verbose >= 1:
        print("Diplaying batch as: % s" % args.batch)
else:
    batch=0
if args.watch:
    watch=str(args.watch)
    if verbose >= 1:
        print("Diplaying watch as: % s" % args.watch)
else:
    watch=""
if args.monitor:
    monitor=int(args.monitor)
    if verbose >= 1:
        print("Diplaying monitor as: % s" % args.monitor)
    if search == "":
        sys.exit("Search (-s) parameter required with monitor.  Quitting.")
else:
    monitor=0
if args.delay:
    delay=int(args.delay)
    if verbose >= 1:
        print("Diplaying delay as: % s" % args.delay)
else:
    delay=5
if args.host:
    hostname=str(args.host)
    if verbose >= 1:
        print("Diplaying host as: % s" % args.host)
else:
    hostname = str(subprocess.check_output("hostname", shell=True).decode("utf-8") ).replace("\n","")
############################################
if verbose >= 1:
    print('verbose = ',verbose)
    print('search = ',search)
    print('batch = ',batch)
    print('watch = ',watch)
    print('monitor = ',monitor)
    print('delay = ',delay)
    print('Number of arguments:', len(sys.argv), 'arguments.')
    print('Argument lst:', str(sys.argv))
############################################
data = "output_mode=json"
url = "https://"+str(hostname)+":8089/services/admin/inputstatus/TailingProcessor%3AFileStatus"
cmd = "curl --get -d "+str(data)+" -k --silent -u "+username+":"+password+" "+url
#dd = requests.get(url, headers={'Accept': 'application/json'}, data=data, auth=(username, password), verify=False)

if verbose >= 1:
    print("cmd = "+str(cmd))

if watch != "":
    print("Refreshing every 1s\n\n")
    iter = 0; lpos=0; lsize=0; cpos=0; csize=0; pdiff=0; sdiff=0;tdiff=0;bdiff=0;ltype=0
    while True:
        dd = requests.get(url, headers={'Accept': 'application/json'}, data=data, auth=(username, password), verify=False)
        dd = json.loads(dd.text)["entry"][0]["content"]["inputs"]
        found = False
        for key in dd.keys():
            if key.find(watch) > -1:
                found = True
        if found:
            ss = dd[watch]
            print("["+str(iter)+"]"+watch)
            for x,y in ss.items():
                if "parent" not in str(x):
                    if verbose >=2:
                        print("x = "+str(x)+"\ny = "+str(y))
                    if "position" in str(x):
                        pdiff = int(y) - int(lpos)
                        lpos = int(y)
                        if pdiff > 0 and pdiff != int(y):
                            print("\t"+str(x)+": "+str(y)+"\t+"+Fore.GREEN+str(pdiff)+Style.RESET_ALL+" size increase")
                            tdiff = 0
                        else:
                            print("\t"+str(x)+": "+str(y)+"\t"+Fore.RED+"[no change in last "+str(tdiff)+" sec]"+Style.RESET_ALL )
                            tdiff = tdiff + 1
                    else:
                        print("\t"+str(x)+": "+str(y))
        else:
            print("key '"+str(watch)+"' not found")
        print("\n##############")
        time.sleep(1)
        iter = iter + 1
elif search != "" and monitor == 0:
    dd = requests.get(url, headers={'Accept': 'application/json'}, data=data, auth=(username, password), verify=False)
    dd = json.loads(dd.text)["entry"][0]["content"]["inputs"]
    for key,value in dd.items():
        if "did not match whitelist" not in str(value) and "directory" not in str(value) and "blacklist" not in str(value):
            if search in str(key):
                print("\n"+str(key))
                for x,y in dd[key].items():
                    if "parent" not in str(x):
                        print("\t"+str(x)+": "+str(y))
                print("###############################")
elif int(batch) > 0:
    bCount = 0
    dd = requests.get(url, headers={'Accept': 'application/json'}, data=data, auth=(username, password), verify=False)
    dd = json.loads(dd.text)["entry"][0]["content"]["inputs"]
    for key,value in dd.items():
        if "batch" in str(value):
            print("\n"+str(key))
            bCount = bCount + 1
            for x,y in dd[key].items():
                if "parent" not in str(x):
                    print("\t"+str(x)+": "+str(y))
            print("###############################")
    print("total batch logs: "+str(bCount)+"\n")
elif int(monitor) > 0:  ####################
    mon = {}
    dd = requests.get(url, headers={'Accept': 'application/json'}, data=data, auth=(username, password), verify=False)
    dd = json.loads(dd.text)["entry"][0]["content"]["inputs"]
    for key,value in dd.items():
        #if "did not match whitelist" not in str(value) and "directory" not in str(value) and "blacklist" not in str(value):
        if "percent" in str(value):
            mon[key] = dd[key]['percent']
    while True:            
        dd = requests.get(url, headers={'Accept': 'application/json'}, data=data, auth=(username, password), verify=False)
        dd = json.loads(dd.text)["entry"][0]["content"]["inputs"]
        add = []
        for key,value in dd.items():
            if "percent" in str(value):
                if verbose == 2:
                    print("key = "+str(key))
                found = 0
                lperc=0;cperc=0;name=""
                for mm in mon.keys():
                    if verbose == 2:
                        print("mm = "+str(mm)+" - key = "+str(key))
                    if mm == key:
                        found = 1
                if found == 1:
                    name = str(dd[key])
                    if "percent" in str(dd[key]):
                        cperc = int(dd[key]['percent'])
                    if "percent" in str(mon[key]):
                        lperc = int(mon[key]['percent'])
                    pdiff = int(cperc) - int(lperc)
                    if search in str(key):
                        if pdiff > 0 and cperc <100:
                            breakpoint()
                            print(str(key)+"\t"+str(cperc)+"%\t["+Fore.GREEN+"+"+str(pdiff)+Style.RESET_ALL+"]" )
                        if cperc == 100:
                            print(str(key)+"\t"+str(cperc)+"%\t["+Fore.BLUE+"DONE"+Style.RESET_ALL+"]" )
                        else:
                            print(str(key)+"\t"+str(cperc) )
                else:
                    if search in str(key):
                        if verbose >= 1:
                            print("adding --> "+key)
                        add.append(key)
        for x in add:
            mon[x] = dd[key]['percent']
        time.sleep(delay)
else:
## all
    dd = requests.get(url, headers={'Accept': 'application/json'}, data=data, auth=(username, password), verify=False)
    dd = json.loads(dd.text)["entry"][0]["content"]["inputs"]
    for key,value in dd.items():
        if "did not match whitelist" not in str(value) and "directory" not in str(value) and "blacklist" not in str(value):
            print("\n"+key)
            for x,y in dd[key].items():
                if "parent" not in str(x):
                    print("\t"+str(x)+": "+str(y))

sys.exit()
