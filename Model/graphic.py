#!bin/python
#-*-coding:utf-8-*-

# Program produced by Darnige Eden / Grimaud Arthur / Amelie Gruel / Alexia Kuntz on May 2019
# based on the article by Costa and his colleagues in 2016

# Program modified by Paul Bielle / Lola Denet / Charles Guinot / Tongyuxuan Hui / Wenli Niu on May 2020 
# based on the article by Fleshner and his colleagues in 2010

# Supervised by Dr Charlotte Héricé

###### IMPORTATIONS ######

### If user is on Mac ###
from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

import tkinter as tk
from tkinter import filedialog

import matplotlib.pyplot as plt
from pylab import xticks
from pylab import yticks
import csv
import numpy
import random
import math
import os


###############################
###### GENERAL FUNCTIONS ######
###############################

def whatToDisplay() :
    ### creates a popup window where the user chooses what to display
    # returns a list 
    
    window = tk.Tk()
    window.title("Select what to display")

    choice_F = tk.IntVar(window)
    button_F = tk.Checkbutton(window, text="Firing rates", variable=choice_F)
    button_F.grid(row=0,column=0)
    button_F.select()

    choice_C = tk.IntVar(window)
    button_C = tk.Checkbutton(window, text="Concentrations", variable=choice_C)
    button_C.grid(row=1,column=0)
    button_C.select()

    choice_homeo = tk.IntVar(window)
    button_homeo = tk.Checkbutton(window, text="Homeostatic sleep drive", variable=choice_homeo)
    button_homeo.grid(row=2,column=0)
    button_homeo.select()

    choice_hypno = tk.IntVar(window)
    button_hypno = tk.Checkbutton(window, text="Hypnogram", variable=choice_hypno)
    button_hypno.grid(row=3,column=0)
    button_hypno.select()

    tk.Button(window,text="Done",command=window.quit).grid(column=0,row=4)

    window.mainloop()
    window.destroy()

    to_display = []
    if choice_F.get() == 1 :
        to_display.append("F")
    if choice_C.get() == 1 :
        to_display.append("C")
    if choice_homeo.get() == 1 :
        to_display.append("homeo")
    if choice_hypno.get() == 1 :
        to_display.append("hypno")

    return to_display


def transformData(data,option) :
    ### transforms the data in order to use a more flexible createGraph() function
    # reads data from the simulation or from a CSV file
    # returns dictionary with more general keys ('firing rates', 'concentrations','sem max', etc)
    
    new_data = {}
    new_data["firing rates"] = {}
    new_data["concentrations"] = {}
    if option == 'stdev' :
        for a in ['stdev min','stdev max'] :
            new_data[a] = {}
            for b in ['firing rates','concentrations'] :
                new_data[a][b] = {}
    elif option == 'sem' :
        for c in ['sem min', 'sem max'] :
            new_data[c] = {}
            for d in ['firing rates','concentrations'] :
                new_data[c][d] = {}

    for (variable,values) in data.items() :
        if variable[-2:] == "_F" :
            new_data["firing rates"][variable[:-2]] = values
        elif variable[-2:] == "_C" :
            new_data["concentrations"][variable[:-2]] = values

        elif variable[-10:] == '_stdev_min' :
            if variable[-12:-10] == "_F" :
                new_data['stdev min']["firing rates"][variable[:-12]] = values
            elif variable[-12:-10] == "_C" :
                new_data['stdev min']["concentrations"][variable[:-12]] = values
        elif variable[-10:] == '_stdev_max' :
            if variable[-12:-10] == "_F" :
                new_data['stdev max']["firing rates"][variable[:-12]] = values
            elif variable[-12:-10] == "_C" :
                new_data['stdev max']["concentrations"][variable[:-12]] = values

        elif variable[-8:] == '_sem_min' :
            if variable[-10:-8] == "_F" :
                new_data['sem min']["firing rates"][variable[:-10]] = values
            elif variable[-10:-8] == "_C" :
                new_data['sem min']["concentrations"][variable[:-10]] = values
        elif variable[-8:] == '_sem_max' :
            if variable[-10:-8] == "_F" :
                new_data['sem max']["firing rates"][variable[:-10]] = values
            elif variable[-10:-8] == "_C" :
                new_data['sem max']["concentrations"][variable[:-10]] = values

        elif variable == "time" or variable == "homeostatic" or variable == "hypnogram":
            new_data[variable] = values

    return new_data


def getNeurotransmitters(header) :
    ### get the neurotransmitters for each neuronal population from the header list
    # returns a dictionary with the neuronal populations as keys and the corresponding neurotransmitters
    neurotransmitters = {}
    for element in header : 
        if element[0] != "#" :
            element = element.split("--->")
            neurotransmitters[element[0]] = element[1]
    return neurotransmitters



###################################################
###### CREATING THE DIFFERENT TYPES OF GRAPHS #####
###################################################

def createGraph(data,neurotransmitters,option=0):
    ### Create a graph from one result
    # general function, called by other functions creating graphs 
    # different possible options ('control', 'stdev' or 'sem') leading to different representations

    if option == "control" : 
        to_display = ["F","C","homeo","hypno"]
    else :
        to_display = whatToDisplay()

    ### defines the line style
    if option == "control" :
        line = '--'
        transparency = 0.25
    else :
        line = '-'
        transparency = 1

    ### defines the corresponding colors for the 3 population and 6 populations models
    colors = {
        'wake' : 'g',
        'NREM' : 'r',
        'REM' : 'b',
        'LC' : 'g',
        'DR' : 'gray',
        'VLPO' : 'r',
        'R' : 'b',
        'WR' : 'cyan',
        'SCN' : 'magenta',
        'homeostatic' : 'y',
        'hypnogram' : 'black'
    }
    data = transformData(data,option)
    
    ### defines temporary colors for other models
    listColors = ["cloudy blue", "dust", "warm purple", "lime green", "pink", "lilac", "dark pink", "indigo","forest green","orange","olive green", "brick red", "sea blue", "cream", "scarlet", "raspberry", "greenish blue"]
    for population in data['firing rates'].keys() :
        if population not in colors.keys() :
            colors[population] = "xkcd:"+random.choice(listColors)
    
    ### translate the time initially in s to hours or minutes
    time_ms = []
    time_h = []
    unit = 60*60
    step_hour = 2
    lim = 24.0
    if data['time'][-1] <= 3600 : 
        step_hour = 0.25
        unit=60
        lim = 60.0
    for t in range(int(data['time'][-1])) :
        if t % (60*60*step_hour) == 0 :
            time_ms.append(t)
            time_h.append(int(t)/unit)
    # Add the last value of time axis
    time_ms.append(lim*unit)
    time_h.append(lim)
    
    plt.figure(1, figsize=(13, 8))
    plt.gcf().subplots_adjust(left = 0.08, right = 0.8, hspace = 0.4)

    ### subplot 1 - firing rates
    if 'F' in to_display :
        ax=plt.subplot(3,1,1)
        for (fr,values) in data["firing rates"].items() :
            sub1=plt.plot(data['time'], values, colors[fr], ls=line, alpha=transparency, label=fr)

        # show the standard deviation on the mean graphs
        if option == 'stdev' :
            for stdev in ['stdev min','stdev max'] :
                for (fr, values) in data[stdev]["firing rates"].items() :
                    sub1=plt.plot(data['time'], values, color=colors[fr], linewidth=0.25)
                    sub1=plt.fill_between(data['time'],values,data['firing rates'][fr],color=colors[fr],alpha=0.25)

        # show the standard error of the mean on the mean graphs
        elif option == 'sem' :
            for sem in ['sem min','sem max'] :
                for (fr, values) in data[sem]["firing rates"].items() :
                    sub1=plt.plot(data['time'], values, color=colors[fr], linewidth=0.25)
                    sub1=plt.fill_between(data['time'],values,data['firing rates'][fr],color=colors[fr],alpha=0.25)
        # show sticks, labels, title and legends
        xticks(time_ms,time_h)
        plt.ylabel('Activity (Hz)')
        plt.title('Firing rates ~ Time', fontsize=12, fontweight='bold')
        chartBox = ax.get_position()
        ax.set_position([chartBox.x0, chartBox.y0, chartBox.width, chartBox.height])
        ax.legend(loc='upper center', bbox_to_anchor=((chartBox.width+0.34), (chartBox.height+0.85)), shadow=True, ncol=1) # legend outside graph


    ### subplot 2 - concentrations
    if 'C' in to_display or 'homeo' in to_display:
        ax=plt.subplot(3,1,2)
        if 'C' in to_display :
            for (c,values) in data["concentrations"].items() :
                sub2=plt.plot(data['time'], values, color=colors[c], ls=line, alpha=transparency, label=neurotransmitters[c])
        if 'homeo' in to_display :
            sub2=plt.plot(data['time'],data['homeostatic'],color=colors['homeostatic'], ls=line, alpha=transparency, label="homeostatic")
        xticks(time_ms,time_h)

        # show the standard deviation on the mean graphs
        if option == 'stdev' :
            for stdev in ['stdev min','stdev max'] :
                for (c,values) in data[stdev]["concentrations"].items() :
                    sub2=plt.plot(data['time'], values, color=colors[c], linewidth=0.25)
                    sub2=plt.fill_between(data['time'],values,data['concentrations'][c],color=colors[c],alpha=0.25)

        # show the standard error of the mean on the mean graphs
        elif option == 'sem' :
            for sem in ['sem min','sem max'] :
                for (c,values) in data[sem]["concentrations"].items() :
                    sub2=plt.plot(data['time'], values, color=colors[c], linewidth=0.25)
                    sub2=plt.fill_between(data['time'],values,data['concentrations'][c],color=colors[c],alpha=0.25)
        # show sticks, labels, title and legends
        plt.ylabel("Concentrations (aU)")
        plt.title('Neurotransmitter concentrations ~ Time', fontsize=12, fontweight='bold')
        chartBox = ax.get_position()
        ax.set_position([chartBox.x0, chartBox.y0, chartBox.width, chartBox.height])
        ax.legend(loc='upper center', bbox_to_anchor=((chartBox.width+0.38), (chartBox.height+0.85)), shadow=True, ncol=1) # legend outside graph


    ### subplot 3 - hypnogram
    if 'hypno' in to_display :
        sub3=plt.subplot(3,1,3)
        plt.plot(data['time'],data['hypnogram'], colors['hypnogram'], ls=line, alpha=transparency)
        plt.ylim(-0.5,1.5)
        xticks(time_ms,time_h)
        yticks([0,0.5,1],['NREM','REM','Wake'])
        if data['time'][-1]<=3600: # Rodents models 
            plt.xlabel('Time (min)')
        else : 
            plt.xlabel('Time (h)') # Human model
        plt.ylabel('Hypnogram')
        plt.title('Hypnogram ~ Time', fontsize=12, fontweight='bold')

    if option != "control" :
        plt.show()

       
def createMeanGraphs(files,option=0) :
    ### creates the graph representing the mean of multiple results, and the hypnogram obtained from this mean
    results = []
    for file in files :
        data, header = readCSV(file)
        results.append(data)
    
    neurotransmitters = getNeurotransmitters(header)
    
    if option == "compare_to_control" or option == "control" :    # if the function is called by compareWithControl(), the standard deviation and the standard error of the mean are automatically not displayed
        check_stdev = tk.StringVar()
        check_stdev.set(0)
    else :
        ### user chooses whether to use standard deviation, standard mean of the error or nothing
        window_stdev = tk.Tk()
        window_stdev.title("Display :")
        check_stdev = tk.StringVar(window_stdev)
        tk.Radiobutton(window_stdev,  text="Display the standard deviation", value="std", variable=check_stdev,width=45).pack()
        tk.Radiobutton(window_stdev,  text="Display the standard error of the mean", value="sem", variable=check_stdev,width=45).pack()
        tk.Radiobutton(window_stdev,  text="Nothing", value="no", variable=check_stdev,width=45).pack()
        tk.Button(window_stdev,text="Done",command=window_stdev.quit).pack()
        window_stdev.mainloop()
        window_stdev.destroy()

    # get the mean values for every variable
    mean_data = {}
    stat = {}
    for element in results[0] :
        if element != 'hypnogram' :
            mean_data[element] = []
            stat[element] = []

    for element in mean_data :
        for i in range(len(results[0][element])) :
            stat_tmp = []
            for fic in results :
                stat_tmp.append(fic[element][i])
            stat[element].append(stat_tmp)
        for l in stat[element] :
            tmp = 0
            for val in l :
                tmp += val
            tmp /= len(l)
            mean_data[element].append(tmp)

    # computes the standard deviation
    if check_stdev.get() == 'std' :
        for (variable,values) in stat.items() :
            if variable != 'homeostatic' :
                mean_data[variable+'_stdev_min'] = []
                mean_data[variable+'_stdev_max'] = []
                for k in range(len(values)) :
                    stdev = numpy.std(values[k])
                    mean_data[variable+'_stdev_min'].append(mean_data[variable][k]-stdev)
                    mean_data[variable+'_stdev_max'].append(mean_data[variable][k]+stdev)

    # computes the standard error of the mean
    elif check_stdev.get() == 'sem' :
        for (variable,values) in stat.items() :
            if variable != 'homeostatic' :
                mean_data[variable+'_sem_min'] = []
                mean_data[variable+'_sem_max'] = []
                for k in range(len(values)) :
                    sem = numpy.std(values[k]) / math.sqrt(len(values[k]))
                    mean_data[variable+'_sem_min'].append(mean_data[variable][k]-sem)
                    mean_data[variable+'_sem_max'].append(mean_data[variable][k]+sem)

    # computes the hypnogram according type of model

    mean_data['hypnogram'] = []
    key_wake_C = ""
    key_REM_C = ""
    if 'LC_C' in mean_data.keys() : # 6 populations models
        key_wake_C="LC_C"
        key_REM_C="R_C"
    elif 'wake_C' in mean_data.keys(): # 3 populations models
        key_wake_C="wake_C"
        key_REM_C="REM_C"
    else : 
        print("Unknown population") # if the name of the population is different of 6 and 3 populations models
        return

    for i in range(len(mean_data['time'])):
        if mean_data[key_wake_C][i] < 0.4 :
            if mean_data[key_REM_C][i] > 0.4 :
                mean_data['hypnogram'].append(0.5)
            else :
                mean_data['hypnogram'].append(0)
        else :
            mean_data['hypnogram'].append(1)

    if check_stdev.get() == 'std' :
        createGraph(mean_data, neurotransmitters,'stdev')
    elif check_stdev.get() == 'sem' :
        createGraph(mean_data, neurotransmitters,'sem')
    elif option == "control" :
        createGraph(mean_data,neurotransmitters,option)
    else :
        createGraph(mean_data, neurotransmitters)

        
def compareWithControl() :
    ### compare on a singe graph 1 or the mean of multiple results to 1 or the mean of multiple other results (useful to compare the effect of a microinjection to a control for example)

    ### choose what you want to use as control
    window_control = tk.Tk()
    window_control.title("Use as control :")
    check_control = tk.StringVar(window_control)
    tk.Radiobutton(window_control,  text="One result", value="one", variable=check_control,width=45).pack()
    tk.Radiobutton(window_control,  text="The mean of multiple results", value="mult", variable=check_control,width=45).pack()
    tk.Button(window_control,text="Done",command=window_control.quit).pack()
    window_control.mainloop()
    window_control.destroy()

    ### draws the graph for the control without displaying it
    if check_control.get() == "one" :
        fileControl = filedialog.askopenfilename(initialdir = os.getcwd(),title = "Select control",filetypes = (("CSV files","*.csv"),("all files","*.*")))
        control, header = readCSV(fileControl)
        neurotransmitters = getNeurotransmitters(header)
        createGraph(control,neurotransmitters,'control')
    elif check_control.get() == "mult" :
        filesControl = filedialog.askopenfilenames(initialdir = os.getcwd(),title = "Select control files", filetypes = (("CSV files","*.csv"),("all files","*.*")))
        createMeanGraphs(filesControl,"control")

    ### choose what you want to compare
    window_compare = tk.Tk()
    window_compare.title("Compare to control :")
    check_compare = tk.StringVar(window_compare)
    tk.Radiobutton(window_compare,  text="One result", value="one", variable=check_compare,width=45).pack()
    tk.Radiobutton(window_compare,  text="The mean of multiple results", value="mult", variable=check_compare,width=45).pack()
    tk.Button(window_compare,text="Done",command=window_compare.quit).pack()
    window_compare.mainloop()
    window_compare.destroy()

    ### choose the graph for the result(s) to compare then display both
    if check_compare.get() == "one" :
        file = filedialog.askopenfilename(initialdir = os.getcwd(),title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))
        GraphFromCSV(file)
    elif check_compare.get() == 'mult' :
        files = filedialog.askopenfilenames(initialdir = os.getcwd(),title = "Select files", filetypes = (("CSV files","*.csv"),("all files","*.*")))
        createMeanGraphs(files,"compare_to_control")


        
##########################
###### GET THE DATA ######
##########################
    
def readCSV(file) :
    ### reads the data from a CVS file
    # returns a dictionary with the resuts and a list with the header
    check_header = 0
    tmp = open(file,'r')
    line = tmp.readline().rsplit()
    if line[0][0] == "#" :
        check_header = 1
        header = line
        names = tmp.readline().rsplit()
    else : 
        names = line
        header = "### "
        for name in names :
            header+=name[:-2]+"--->"+name[:-2]+" "
        header = header.rsplit()
    tmp.close()

    results={}
    for n in names :
        results[n]=[]

    with open(file) as f:
        if check_header == 1 :
            f.readline()
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader :
            for (name,element) in row.items() :
                results[name].append(float(element))
    return results, header


def GraphFromCSV(file) :
    ### creates a graph from a CSV file
    data, header = readCSV(file)
    neurotransmitters = getNeurotransmitters(header)
    createGraph(data, neurotransmitters)


def GraphFromSim(sim,header):
    ### creates a graph from the simulation
    data = {}
    for var in sim :
        data[var[0]] = var[1:]
    header = header.rsplit()
    neurotransmitters = getNeurotransmitters(header)
    createGraph(data, neurotransmitters)
