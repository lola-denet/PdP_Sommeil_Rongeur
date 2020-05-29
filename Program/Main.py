#!bin/python
#-*-coding:utf-8-*-

# Program produced by Darnige Eden / Grimaud Arthur / Amelie Gruel / Alexia Kuntz on May 2019
# based on the article by Costa and his colleagues in 2016

# Program modified by Paul Bielle / Lola Denet / Charles Guinot / Tongyuxuan Hui / Wenli Niu on May 2020 
# based on the article by Fleshner and his colleagues in 2010

# Supervised by Dr Charlotte Héricé

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

from manage_parameters import *
from SleepRegulationOOP import NeuronalPopulation
from SleepRegulationOOP import HomeostaticSleepDrive
from SleepRegulationOOP import Network
from SleepRegulationOOP import Injection
from graphic import *
import os

network = Network()

def loadModel():
    ### initiates the network using the 4 dictionnaries returned by read_parameters() (imported from manage_parameters)
    # creates the object Network and its compartments (objects NeuronalPopulation, Connection and HomeostaticSleepDrive
    global network


    pop,cycle,sim,conn,inj=read_parameters(filedialog.askopenfilename(initialdir = os.getcwd(),title = "Select file",filetypes = (("text files","*.txt"),("all files","*.*"))))
    network = Network(sim)   

    for key in pop.keys():
        network.addNP(pop[key])
    print("### Neuronal Populations OK ###\n")
    
    for key in cycle.keys():
        network.addHSD(cycle[key])
    print("### Homeostatic Sleep Drive OK ###\n")

    for key in inj.keys():
        network.addINJ(inj[key])
    print("### Microinjections OK ###\n")
    
    for pop_ext in conn.keys() :
        i = 0
        for pop_source in conn[pop_ext] :
            if pop_ext == 'homeostatic' or pop_ext == 'HSD':
                network.addNPConnection("NP-HSD",pop_source,"HSD",cycle[pop_ext]["g_NT_pop_list"][i])
            elif pop_source == 'homeostatic' or pop_source == 'HSD':
                network.addNPConnection("HSD-NP","HSD",pop_ext,pop[pop_ext]["g_NT_pop_list"][i])
            else :
                network.addNPConnection("NP-NP",pop_source,pop_ext,pop[pop_ext]["g_NT_pop_list"][i])
            i+=1
    print("### Connections OK ###\n")
    
    network.getSimParamFrame(runMenu).grid(column = 0, row = 1)


def doStats():
    filez=filedialog.askopenfilenames(initialdir = os.getcwd(),title = "Select results files",filetypes = (("csv files","*.csv"),("all files","*.*")))
    script = "Rscript Stats.r"
    run = script

    for selection in filez:
        run = run + " " + selection

    os.system(run)



#----------- Window initialization -----------

window = tk.Tk()
window.title("SR sim")
# Get screen dimensions and resize the window
widthScreen = window.winfo_screenwidth()
heightScreen = window.winfo_screenheight()
window.geometry("{}x{}".format(int(widthScreen), int(heightScreen)))

n = ttk.Notebook(window,width = int(widthScreen), height = int(heightScreen))   # Creation of tab system
n.pack()

mainMenu = ttk.Frame(n,relief = tk.SUNKEN)       # Add main tab
mainMenu.pack(fill="both")

paramMenu = ttk.Frame(n,relief = tk.SUNKEN)       # Add parameters tab
paramMenu.pack(fill="both", expand=True)

runMenu = ttk.Frame(n,relief = tk.SUNKEN)       # Add run tab
runMenu.pack(fill="both")

visuMenu = ttk.Frame(n,relief = tk.SUNKEN)       # Add visualization tab
visuMenu.pack(fill="both")

statMenu = ttk.Frame(n,relief = tk.SUNKEN)       # Add statistics tab
statMenu.pack(fill="both")

n.add(mainMenu, text='Main')
n.add(paramMenu, text='Parameters')
n.add(runMenu, text='Run')
n.add(visuMenu, text='Visualization')
n.add(statMenu, text='Statistics')

#-----------Main menu widgets---------------

tk.Button(mainMenu, text="Load model",bg='lightblue', command=lambda:loadModel(),width=25).grid(column=0, row=0)

b = tk.Button(mainMenu, text="Display network", command=lambda: network.displayGraph(),width=25)
b.grid(column=0, row=1)

b = tk.Button(mainMenu, text="Display connections", command=lambda: network.displayConnections(),width=25)  # Useful to debug
b.grid(column=0, row=2)

txt = tk.Entry(mainMenu,width=25)       # Useful to debug
txt.insert(END, "Enter compartment name")
txt.grid(column=1, row=3)


b = tk.Button(mainMenu, text="Print parameters and type of compartment", command=lambda: network.printAttrType(txt.get()),width=45) # Useful to debug
b.grid(column=0, row=3)



#--------------Param menu widgets-------------------

b = tk.Button(paramMenu, text="Add Object to Network", command=lambda: network.addObjToModel(network),width=25)
b.grid(column=0, row=0)

b = tk.Button(paramMenu, text="Display Compartments Parameters",bg='lightblue', command=lambda: network.displayCompParam(paramMenu))
b.grid(column=0, row=4)

b = tk.Button(paramMenu, text="Save Parameters", command=lambda: write_parameters(filedialog.asksaveasfile(title="Save as", initialdir=os.getcwd(), mode="w", defaultextension=".txt"),network))
b.grid(column=0, row = 6)

b = tk.Button(paramMenu, text="Add injection",bg='lemonchiffon', command=lambda:network.getInjectionCreationWindow())
b.grid(column=0, row = 7)

#--------------Run menu widgets-------------------

b = tk.Button(runMenu, text="Run sim",bg='lightblue', command=lambda: network.getResults(),width=25)
b.grid(row=0)
b = tk.Button(runMenu, text="Select variables to save(WIP)", command=lambda: network.displayCompVar().grid(column=0, row=2),width=25)
b.grid(row=2)

#--------------Visualization menu widgets-------------------

b = tk.Button(visuMenu, text="Visualize the results from the simulation",bg='lightblue', command=lambda: GraphFromSim(network.results,network.fileHeader()),width=75).grid(column=0, row=0)
b = tk.Button(visuMenu, text="Visualize precedent results", command=lambda: GraphFromCSV(filedialog.askopenfilename(initialdir = os.getcwd(),title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))),width=75).grid(column=0, row=1)
b = tk.Button(visuMenu, text="Visualize a mean graph from multiple results", command=lambda: createMeanGraphs(filedialog.askopenfilenames(initialdir = os.getcwd(),title = "Select files", filetypes = (("CSV files","*.csv"),("all files","*.*")))),width=75).grid(column=0,row=2)
b = tk.Button(visuMenu, text="Compare results to a control", command=lambda: compareWithControl(),width=75).grid(column=0,row=3)

#--------------Statistics menu widgets-------------------

b = tk.Button(statMenu, text="Select results files", command=lambda: doStats(),width=25)
b.grid(column=0, row=0)

window.mainloop()
