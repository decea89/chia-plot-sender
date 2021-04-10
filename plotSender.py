import subprocess
import time
import sys

from datetime import datetime


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


def run_list() -> str:
    return str(subprocess.check_output(['ls', '-l']))

def get_path_size(path: str) -> float:
    path_info = str(subprocess.check_output(['df',path]))
    unformated_usage = path_info.split('\\n')[1].split('%')[0]
    
    usage = unformated_usage[-2:-1].replace(" ","")
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

    plot_name = 'plot-k32'+(total_plots.split('\\n')[2+path_index].split('plot-k32')[1])
    if plot_name.find("plot.2.temp") != -1:
        plot_name = ""
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
    return subprocess.Popen("mv" + " " + fullPath + " " + dest_path, shell=True)
    

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
                    time.sleep(5 * 60)
                    continue


                i = 0
                total_plots = get_total_plots()
                plots_available = parse_total_plots(total_plots)
                if plots_available < 1:
                    print(f'There is no plots available, searchin again in a while... {datetime.now()}')
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
                            print(f'Sending new plot: {delivery.plot} to {delivery.path} {datetime.now()}')
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
