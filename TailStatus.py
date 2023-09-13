import os,sys,subprocess,pdb,json,time
from termcolor import colored
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
#
url="https://192.168.11.22:8089/services/admin/inputstatus/TailingProcessor%3AFileStatus"
user = ""
pw = ""
cmd = "curl --get -d output_mode=json -k --silent -u "+user+":"+pw+" "+url

## search 
search = "cisco"
dd = json.loads(subprocess.check_output(cmd, shell=True).decode('utf-8') )["entry"][0]["content"]["inputs"]
for key,value in dd.items():
    if "did not match whitelist" not in str(value) and "directory" not in str(value) and "blacklist" not in str(value):
        if search in str(key):
            print("\n"+str(key))
            for x,y in dd[key].items():
                if "parent" not in str(x):
                    print("\t"+str(x)+": "+str(y))

## watch
watch="/var/log/cisco/rv340/firewall.log"
iter = 0; lpos=0; lsize=0; cpos=0; csize=0; pdiff=0; sdiff=0
while True:
    dd = json.loads(subprocess.check_output(cmd, shell=True).decode('utf-8') )["entry"][0]["content"]["inputs"]
    ss = dd[watch]
    print("["+str(iter)+"]"+watch)
    for x,y in ss.items():
        if "parent" not in str(x):
            if "position" in str(x):
                pdiff = int(y) - int(lpos)
                lpos = int(y)
                if pdiff > 0 and pdiff != int(y):
                    print("\t"+str(x)+": "+str(y)+"\t+"+Fore.RED+str(pdiff)+Style.RESET_ALL)
                else:
                    print("\t"+str(x)+": "+str(y))
            print("\n##############")
    time.sleep(1)
    iter = iter + 1

## all
dd = json.loads(subprocess.check_output(cmd, shell=True).decode('utf-8') )["entry"][0]["content"]["inputs"]
for key,value in dd.items():
    if "did not match whitelist" not in str(value) and "directory" not in str(value) and "blacklist" not in str(value):
        print("\n"+str(key))
        for x,y in dd[key].items():
            if "parent" not in str(x):
                print("\t"+str(x)+": "+str(y))

sys.exit()
