import subprocess
import time
import sys
import re

from typing import Optional
from datetime import datetime

import requests

#Telegram bot stuff. Replace API_KEY and CHAT_ID

TELEGRAM_BOT_API_KEY = 'XXXXXXXXXX:aaaaaaaabbbbbbbcccccccddddddeeeeeee'
TELEGRAM_CHAT_ID = 'YYYYYYYYY'
TELEGRAM_SEND_MESSAGE_URL = "https://api.telegram.org/bot{}/sendMessage".format(
    TELEGRAM_BOT_API_KEY
)
# PUT HERE YOUR PATHS (DEST_PATHS)
# THIS SCRIPT WILL SEND PLOTS TO MOUNTED DEVICES WITH AN USAGE LESS THAN 97% TO AVOID OUT_OF_SPACE DURING THE COPY

DEST_PATHS = ['/home/dechin/sharedPlots/hdd','/home/dechin/sharedPlots/hdd1','/home/dechin/sharedPlots/hdd8tb-1','/home/dechin/sharedPlots/hdd3']

# PUT HERE THE PATH WHERE PLOTS ARE BEING STORED INTO THE PLOTTER

SOURCE_PATH = '/mnt/hddunico/'




MINUTES_TO_SLEEP = 2

class Delivery:
    path = ""
    plot = ""
    index = -1
    process = None

def send_telegram_message(text, chat_id):
    try:
        requests.post(TELEGRAM_SEND_MESSAGE_URL, json={'chat_id': chat_id, 'text': text})
    except Exception as e:
        print(f'Something was wrong\nMessagge that was supposed to be sent: {text}\nError: {e.message}')

def filter(datalist):
    tuples = [val for val in datalist
        if re.search(r'\.plot', val)]
    #for t in tuples:
        #prinln(f'{t}')
    return tuples

def run_list() -> str:
    return str(subprocess.check_output(['ls', '-l']))

def get_path_size(path: str) -> float:
    path_info = str(subprocess.check_output(['df',path]))
    unformated_usage = path_info.split('\\n')[1].split('%')[0]
    
    usage = (unformated_usage[-2]+unformated_usage[-1]).replace(" ","")
    print(f'{path} has an usage of {usage}%')

    usagef = float(usage)
    return usagef


def parse_total_plots(total_plots: str) -> float:      
    return len(total_plots.split('\\n')) -2  # ???????????????????


def get_total_plots() -> Optional[float]:
    try:
        total_plots = run_list()
    except FileNotFoundError:
        print('ERROR: Cannot run ls -l!')
        return None

    return total_plots

def get_plot(total_plots, path_index):
    
    tuples = total_plots.split('\\n')  
    filtered = filter(tuples)
    #for fe in filtered:
        #print(f'{fe}\n')    
    plot_name = ""
    i = 0

    for t in filtered:
        if (t.find("plot.2.temp") == -1):
            if (i==path_index):
                plot_name = 'plot-k32'+(t.split('plot-k32')[1])
                f_ind = plot_name.find(".plot")
                plot_name = plot_name[0:f_ind+5]
                break
            i+=1

            #print(plot_name)

    return plot_name

def get_available_paths():

    paths = []
    i = 0
    o_paths = DEST_PATHS

    for p in o_paths:
        if get_path_size(p) > 97:
         continue
        paths.append(p)
        i+=1

    return paths


def send_plot(plot_name,path_name):
    dest_path = path_name
    fullPath = SOURCE_PATH + plot_name
    try:
        process = subprocess.Popen("mv" + " " + fullPath + " " + dest_path, shell=True)
        return process
    except Exception as e:
        message = f'Plot sender ha faileao enviando un plot.\n Plot: {pot_name}\n Path: {dest_path}\n Error: {e.message}\n{datetime.now()}'
        send_telegram_message(message,TELEGRAM_CHAT_ID)
        return None

def still_sending(p):

    poll = p.poll() 

    return poll is None # true = ongoing , false = process ended

def main():
    total_plots = '' 
    paths = []
    deliveries = []
    concurrence_level = 0 # 0 = max concurrence 
    
    if(len(sys.argv) > 1):
        try:
            concurrence_level = float(sys.argv[1])
        except Exception as e:
            print(f'wrong params! Sender will use max concurrece level.')

    while True:

            if len(deliveries) > 0:

                for d in deliveries:
                    if still_sending(d.process):
                        print(f'Still sending plot {d.index}: {d.plot} to: {d.path} ')
                    else:
                        print(f'Delivery ended for {d.plot} {datetime.now()}')
                        deliveries.remove(d)
                time.sleep(MINUTES_TO_SLEEP * 60)

            else:

                paths = get_available_paths()
                #paths = DEST_PATHS                
                if len(paths) < 1:
                    print(f'There is no space available at dest paths, add more paths... {datetime.now()}')
                    message = f'out of storage\n{datetime.now()}'
                    send_telegram_message(message,TELEGRAM_CHAT_ID)
                    time.sleep(60 * 60)
                    continue


                i = 0
                total_plots = get_total_plots()
                plots_available = parse_total_plots(total_plots)
                if plots_available < 1:
                    #print(f'There is no plots available, searchin again in a while... {datetime.now()}')
                    time.sleep(5 * 60)
                    continue

                for pa in paths:

                    if plots_available >= i+1:   
                        delivery = Delivery()
                        delivery.path = pa
                        delivery.index = i
                        delivery.plot = get_plot(total_plots, i)
                        if(delivery.plot != ""):
                            delivery.process = send_plot (delivery.plot, delivery.path)
                            print(f'Sending new plot: {delivery.plot} to {delivery.path} at {datetime.now()}')
                            deliveries.append(delivery)
                        else:
                            print(f'There is no plots available, searchin again in a while... {datetime.now()}')
                            time.sleep(5 * 60)

                    if(concurrence_level == 0 or (concurrence_level>0 and i < concurrence_level-1)):
                        i+=1
                    else: 
                        break                


if __name__ == '__main__':
    main()
