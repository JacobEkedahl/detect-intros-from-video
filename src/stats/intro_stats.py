import matplotlib.pyplot as plt

import utils.extractor as extractor
import utils.file_handler as file_handler
import utils.time_handler as time_handler


def plot_intros():
    intros = extractor.get_intros_from_data()
    only_valid_intros = [x for x in intros if not x["end"] == "00:00:00"]
    x_data = map(get_start_time_seconds, only_valid_intros) 
    y_data = map(get_size_from_intro, only_valid_intros) 
    # naming the x axis
    plt.xlabel('Start time of intro (Seconds)') 
    # naming the y axis 
    plt.ylabel('Length of intro (Seconds)')
    plt.grid(True)
    plt.scatter(list(x_data), list(y_data)) 
    plt.show()

def plot_hist_sizes():
    intros = extractor.get_intros_from_data()
    only_valid_intros = [x for x in intros if not x["end"] == "00:00:00"]
    x_data = list(map(get_size_from_intro, only_valid_intros))
    plt.xlabel('Length of intro (Seconds)') 
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.hist(x_data, bins=40)
    plt.show()

def plot_hist_frequency():
    intros = extractor.get_intros_from_data()
    only_valid_intros = [x for x in intros if not x["end"] == "00:00:00"]
    x_data = list(map(get_start_time_seconds, only_valid_intros))
    plt.xlabel('Start time of intro (Seconds)') 
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.hist(x_data, bins=60)
    plt.show()

def plot_all_intros():
    x_titles = ['Start time of intro (Seconds)', 'Length of intro (Seconds)']
    y_title = 'Frequency'
    titles = ['Start times of intros','Lengths of intros']
    colors = ['blue', 'blue']
    bins = [60, 40]
    intros = extractor.get_intros_from_data()
    only_valid_intros = [x for x in intros if not x["end"] == "00:00:00"]
    x_size = list(map(get_size_from_intro, only_valid_intros))
    x_start = list(map(get_start_time_seconds, only_valid_intros))
    x_data = [x_start, x_size]
    fig, axs = plt.subplots(1, 2)
    axs = axs.ravel()

    for idx, ax in enumerate(axs):
        ax.hist(x_data[idx], bins=bins[idx], fc=colors[idx])
       # ax.set_title(titles[idx])
        ax.set_xlabel(x_titles[idx])
        ax.set_ylabel(y_title)
        ax.grid()
    plt.tight_layout()
    plt.show()


def get_size_from_intro(intro):
    start = time_handler.timestamp(intro["start"]) / 1000
    end = time_handler.timestamp(intro["end"]) / 1000
    return abs(start - end)

def get_start_time_seconds(intro):
    return time_handler.timestamp(intro["start"]) / 1000
