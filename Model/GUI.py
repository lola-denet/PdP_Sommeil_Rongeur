#!bin/python
#-*-coding:utf-8-*-

# 05/12/19
# Authors: Darnige Eden / Grimaud Arthur / Amelie Gruel / Alexia Kuntz


#######################IMPORTATIONS########################

#Calculation
import numpy as np ### not necessary
#Gaphical interface
import tkinter as tk
from tkinter import *
from tkinter import filedialog
#Graph generation
from graphviz import Digraph

from functools import partial
import os

class NetworkGUI:

    #---------------Display Compartement Parameters-----------------------

    def displayCompParam(self, windowTemp):
        window = windowTemp
        widthScreen = window.winfo_screenwidth()
        heightScreen = window.winfo_screenheight()

        # Canvas creation

        container = ttk.Frame(window, relief=tk.SUNKEN)
        canvas = tk.Canvas(container, width=widthScreen*0.9, height=heightScreen*0.9, bg='white')
        scrollbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)
        i = 0
        for comp in self.compartments.values():
            i += 10
            frame = self.getCompartmentFrame(comp, scrollable_frame)
            frame.grid(column=i, row=0)
            canvas.create_window(0, 0)

        container.grid()
        canvas.grid(column=0,row=2, rowspan=2)
        scrollbar.grid(column=0,row=1,sticky='we')
        window.mainloop()

    def getCompartmentFrame(self, comp, frame):

        i = 0
        compFrame = Frame (frame)

        lbl = Label(compFrame, text=comp.name)
        lbl.config(font=("Courier", 15))
        lbl.grid(column=0, row=0)

        def callback(attr, attrB):
            try:
                if attr == "F" or  attr =="C" or attr =="h":
                    comp.__dict__[attr] = [float(attrB.get()),0,0,0,0]
                # elif attr == "beta":
                #     print("beta")
                else:
                    comp.__dict__[attr] = float(attrB.get())
                print (attrB.get())
            except ValueError:
                print("Var set as str")
                comp.__dict__[attr] = str(attrB.get())
                print (attrB.get())


        def callbackW(weight, c):
            try:
                c.__dict__["weight"]=float(weight.get())
                print (weight.get())
                print("type(c.weight):",type(c.weight),c.weight)
            except ValueError:
                print("Var set as str")
                comp.__dict__[attr].set(str(weight.get()))
                print (weight.get())

        for attr, value in comp.__dict__.items():

            attrB = attr #making a copy of attr for trace


            attrB = StringVar()
            attrB.set(value)
            attrB.trace("w", lambda name, index, mode,attr=attr, attrB=attrB: callback(attr, attrB))


            if isinstance(value, list) and len(value) > 0 and attr == "connections": #If connection liste
                for c in value:
                    i += 1

                    weight = StringVar()
                    weight.set(c.weight)

                    lbl = Label(compFrame, text="connection: ").grid(column=0, row=i)

                    lbl = Label(compFrame, text=c.source.name).grid(column=1, row=i)

                    lbl = Label(compFrame, text=c.target.name).grid(column=2, row=i)

                    # entry = Entry(compFrame,width=10)
                    # entry.config(textvariable=c.weight)
                    # entry.grid(column=3, row=i)
                    
                    # e.delete(0,END)
                    # e.insert(END, weight)
                    
                    e = Entry(compFrame, width=10)
                    e.config(textvariable=weight)
                    e.grid(column=3, row=i)
                    weight.trace("w", lambda name, index, mode, weight=weight, c=c: callbackW(weight, c))

            elif attr == "name":
                i += 1
                lbl = Label(compFrame, text=attr)
                lbl.grid(column=0, row=i)
                txt = Entry(compFrame, width=10)
                txt.insert(END, value)
                txt.grid(column=1, row=i)
            elif attr == "promoting":
                i += 1
                lbl = Label(compFrame, text=attr)
                lbl.grid(column=0, row=i)
                txt = Entry(compFrame, width=10)
                txt.insert(END, value)
                txt.grid(column=1, row=i)
            elif attr == "F" or attr == "C" or attr == "h":
                i += 1
                lbl = Label(compFrame, text=attr)
                lbl.grid(column=0, row=i)
                txt = Entry(compFrame, width=10)
                txt.config(textvariable=attrB)
                txt.delete(0,END)
                txt.insert(END, value[0])
                txt.grid(column=1, row=i)
            else:
                i += 1
                lbl = Label(compFrame, text=attr)
                lbl.grid(column=0, row=i)
                txt = Entry(compFrame, width=10)
                txt.config(textvariable=attrB)
                txt.delete(0,END)
                txt.insert(END, value)
                txt.grid(column=1, row=i)

        #b = Button(compFrame, text="Apply changes", command=lambda: self.saveAndClose(var,window),width=25).grid(column=2, row=0)


        return compFrame

    #---------------Display simulation parameters---------------------------


    def getSimParamFrame(self, window):


        def callbackT(T):
            self.T = float(T.get())
            print (T.get())

        def callbackres(res):
            self.res = float(res.get())
            self.dt = 1E3/self.res
            print (res.get())

        def callbackSaveRate(saveRate):
            self.saveRate = float(saveRate.get())
            print (saveRate.get())

        def callbackMean(mean):
            self.mean = float(mean.get())
            print (mean.get())

        def callbackStd(std):
            self.std = float(std.get())
            print (std.get())

        T = StringVar()
        T.trace("w", lambda name, index, mode, T=T: callbackT(T))

        res = StringVar()
        res.trace("w", lambda name, index, mode, res=res: callbackres(res))

        saveRate = StringVar()
        saveRate.trace("w", lambda name, index, mode, saveRate=saveRate: callbackSaveRate(saveRate))

        mean = StringVar()
        mean.trace("w", lambda name, index, mode, mean=mean: callbackMean(mean))

        std = StringVar()
        std.trace("w", lambda name, index, mode, std=std: callbackStd(std))

        frame = Frame(window)

        resMethod = StringVar()
        optMethod = ["Euler", "RK4"]

        def changeMethod(new):
            resMethod = new
            print(resMethod)
            self.resMethod = new



        lbl = Label(frame, text="Select Resolution Method").grid(column=0, row=0)
        optMenu = OptionMenu(frame, resMethod, *optMethod, command=changeMethod).grid(column=1, row=0)


        lbl = Label(frame, text="T").grid(column=0, row=1)
        lbl = Label(frame, text="T (s)").grid(column=0, row=1)
        e = Entry(frame, textvariable=T)
        e.insert(END, self.T)
        e.grid(column=1, row=1)

        lbl = Label(frame, text="res (iterations/s)").grid(column=0, row=2)
        e = Entry(frame, textvariable=res)
        e.insert(END, self.res)
        e.grid(column=1, row=2)

        lbl = Label(frame, text="Save Rate (in Steps)").grid(column=0, row=3)
        e = Entry(frame, textvariable=saveRate)
        e.insert(END, self.saveRate)
        e.grid(column=1, row=3)

        lbl = Label(frame, text="Mean noise (Hz)").grid(column=0, row=4)
        e = Entry(frame, textvariable=mean)
        e.insert(END, self.mean)
        e.grid(column=1, row=4)

        lbl = Label(frame, text="Std noise (Hz)").grid(column=0, row=5)
        e = Entry(frame, textvariable=std)
        e.insert(END, self.std)
        e.grid(column=1, row=5)


        def callbackThresholdWake(std):
            self.wakeThreshold = float(std.get())
            print (std.get())

        thresholdWake = StringVar()
        thresholdWake.trace("w", lambda name, index, mode, thresholdWake=thresholdWake: callbackThresholdWake(thresholdWake))

        lbl = Label(frame, text="threshold Wake").grid(column=0, row=6)

        e = Entry(frame, textvariable=thresholdWake)
        e.insert(END, self.wakeThreshold)
        e.grid(column=1, row=6)


        def callbackThresholdREM(std):
            self.REMThreshold = float(std.get())
            print (std.get())

        thresholdREM = StringVar()
        thresholdREM.trace("w", lambda name, index, mode, thresholdREM=thresholdREM: callbackThresholdREM(thresholdREM))

        lbl = Label(frame, text="threshold REM").grid(column=0, row=7)

        e = Entry(frame, textvariable=thresholdREM)
        e.insert(END, self.REMThreshold)
        e.grid(column=1, row=7)

        return frame





    #---------------Display Compartement Variables for Recorders  /!\ -----------------------

    def displayCompVar(self):
        window = Tk()
        var = 0
        cb = Checkbutton(window, text = "FiringRate", width = 20, variable=var, onvalue=["wake","F"], offvalue=0).grid(column=1, row=0)
        b = Button(window, text="Create Compartment", command=lambda: self.saveAndClose(var,window),width=25)
        b.grid(column=2, row=0)
        window.mainloop()


    def saveAndClose(self,param,window):
        self.results = param
        window.destroy()
        print(self.results)

    #-----------Display window for the creation of new compartment/connection------------
        
    def addObjToModel(self, network):
        window = Toplevel()
        window.geometry('800x500')
        window.title("Add object")
        options = ["Neuronal Population", "Homeostatic Sleep Drive", "Connection"]
        var = StringVar()
        Label(window, text="Please choose which type of compartment you want to add :").grid(column=1, row=0)
        optMenu = OptionMenu(window, var, *options, command=lambda naz: self.getCreateObjFrame(naz, window, optMenu, network).grid(column=3, row=4))
        optMenu.place(x=30, y=30)
        b = Button(window, text="Task completed", command=lambda: window.destroy(),width=25)
        b.place(x=30, y=300)
    def getCreateObjFrame(self, selection, window, optMenu, network):
        frame = Frame (window)
        if selection == "Neuronal Population":

            lbl = Label(frame, text="name").grid(column=0, row=0)
            ety1 = Entry(frame, width=10)
            ety1.grid(column=1, row=0)

            lbl = Label(frame, text="F").grid(column=0, row=1)
            ety2 = Entry(frame, width=10)
            ety2.grid(column=1, row=1)

            lbl = Label(frame, text="C").grid(column=0, row=2)
            ety3 = Entry(frame, width=10)
            ety3.grid(column=1, row=2)

            lbl = Label(frame, text="F_max").grid(column=0, row=3)
            ety4 = Entry(frame, width=10)
            ety4.grid(column=1, row=3)

            lbl = Label(frame, text="beta").grid(column=0, row=4)
            ety5 = Entry(frame, width=10)
            ety5.grid(column=1, row=4)

            lbl = Label(frame, text="alpha").grid(column=0, row=5)
            ety6 = Entry(frame, width=10)
            ety6.grid(column=1, row=5)

            lbl = Label(frame, text="tau_pop").grid(column=0, row=6)
            ety7 = Entry(frame, width=10)
            ety7.grid(column=1, row=6)

            lbl = Label(frame, text="neurotransmitter").grid(column=0, row=7)
            ety8 = Entry(frame, width=10)
            ety8.grid(column=1, row=7)

            lbl = Label(frame, text="gamma").grid(column=0, row=8)
            ety9 = Entry(frame, width=10)
            ety9.grid(column=1, row=8)

            lbl = Label(frame, text="tau_NT").grid(column=0, row=9)
            ety10 = Entry(frame, width=10)
            ety10.grid(column=1, row=9)
            
            lbl = Label(frame, text="promoting").grid(column=0, row=10)
            ety11 = Entry(frame, width=10)
            ety11.grid(column=1, row=10)
 
            b = Button(frame, text="Create", command=lambda: self.readAndCreateComp(frame,
                [ety1.get(), ety2.get(), ety3.get(), ety4.get(), ety5.get(), ety6.get(), ety7.get(), ety8.get(), ety9.get(), ety10.get(), ety11.get()],
                "NP"),width=25).grid(column=0, row=11)

        if selection == "Homeostatic Sleep Drive":

            lbl = Label(frame, text="h").grid(column=0, row=0)
            ety1 = Entry(frame, width=10)
            ety1.grid(column=1, row=0)

            lbl = Label(frame, text="H_max").grid(column=0, row=1)
            ety2 = Entry(frame, width=10)
            ety2.grid(column=1, row=1)

            lbl = Label(frame, text="tau_hw").grid(column=0, row=2)
            ety3 = Entry(frame, width=10)
            ety3.grid(column=1, row=2)

            lbl = Label(frame, text="tau_hs").grid(column=0, row=3)
            ety4 = Entry(frame, width=10)
            ety4.grid(column=1, row=3)

            lbl = Label(frame, text="theta").grid(column=0, row=4)
            ety5 = Entry(frame, width=10)
            ety5.grid(column=1, row=4)

            b = Button(frame, text="Create", command=lambda: self.readAndCreateComp(frame,
                [ety1.get(), ety2.get(), ety3.get(), ety4.get(), ety5.get()], "HSD"),width=25).grid(column=0, row=10)

        if selection == "Connection":

            compsNames = []
            target = StringVar()
            source = StringVar()
            Type = StringVar()
            weightVal = 0

            def changeTarget(new):
                target = new
                print(target)

            def changeSource(new):
                source = new
                print(source)

            def changeType(new):
                Type = new
                print(Type)

            for c in self.compartments.keys():
                compsNames.append(c)

            types = ["NP-NP","HSD-NP","NP-HSD"]

            lbl = Label(frame, text="Select Connection Type").grid(column=0, row=0)
            optMenu = OptionMenu(frame, Type, *types, command=changeType).grid(column=1, row=0)

            lbl = Label(frame, text="Select Source Compartment").grid(column=0, row=1)
            optMenu = OptionMenu(frame, source, *compsNames, command=changeSource).grid(column=1, row=1)

            lbl = Label(frame, text="Select Target Compartment").grid(column=0, row=2)
            optMenu = OptionMenu(frame, target, *compsNames, command=changeTarget).grid(column=1, row=2)

            lbl = Label(frame, text="theta_X").grid(column=0, row=3)
            e = Entry(frame)
            e.grid(column=1, row=3)

            b = Button(frame, text="Create", command=lambda: 
                       [self.addNPConnection(Type.get(), source.get(), target.get(), e.get()),
                        frame.destroy()],width=25).grid(column=0, row=4)
             
        return frame

    def readAndCreateComp(self,window,valuelist,compType):
        compParam = {}
        i = 0
        if compType == "NP":
            attrlist = ["name","F","C","F_max","beta","alpha","tau_pop","neurotransmitter",
                        "gamma","tau_NT","promoting"]
            while i < len(valuelist):
                compParam[attrlist[i]] = valuelist[i]
                i += 1
            print(compParam)
            self.addNP(compParam)
        elif compType == "HSD":
            attrlist = ["h", "H_max", "tau_hw", "tau_hs", "theta"]
            while i < len(valuelist):
                compParam[attrlist[i]] = valuelist[i]
                i += 1
            print(compParam)
            self.addHSD(compParam)
            
        window.destroy()
   
    #------------------------------Injection settings---------------------------------------

    def getInjectionCreationWindow(self):

        window = Toplevel()
        window.title('Type of injection')
       
        connAvailable = []
        connAvailableStr = []
        connStr = StringVar()
    
        def changeConn(new):
            connStr = new
            print(connStr, "type", type(connStr))

        print(self.compartments)
        for c in self.compartments.keys():
            if c not in self.nlist:
                for i in self.compartments[c].connections:
                    if i.type == "NP-NP":
                        connAvailableStr.append("Injection of: "+str(i.source.neurotransmitter)+" in "+str(i.target.name))
                        connAvailable.append(i)

        def getName(window, name):
            window.destroy()
            
            top = Toplevel()  
            top.title('Injection parameters')  
            print(name)
            a = name[14:]
            i = a.index(" ")
            neuro = a[:i]
            # print(a[:i])
            print(neuro)
            
            injType = StringVar()
            optType = ["Agonist", "Antagonist"]
            
            def changeInjType(new):
                injType = new
                print(injType)
    
            def getConnObject(name):
                print("return:::", connAvailable[connAvailableStr.index(name)], "type", type(connAvailable[connAvailableStr.index(name)]))
                return connAvailable[connAvailableStr.index(name)]
            
            lbl = Label(top, text="Select type").grid(column=0, row=0)
            optMenu = OptionMenu(top, injType, *optType, command=changeInjType).grid(column=1, row=0)
            print(injType.get())
        
            lbl = Label(top, text="P0").grid(column=0, row=1)  
            e1 = Entry(top)
            e1.insert(END, self.compartments[neuro].agoniste)
            e1.grid(column=1, row=1)
           
            lbl = Label(top, text="Q0").grid(column=0, row=2)  
            e5 = Entry(top)
            e5.insert(END, self.compartments[neuro].antagoniste)
            e5.grid(column=1, row=2)
    
            lbl = Label(top, text="TauInj").grid(column=0, row=3)
            e2 = Entry(top)
            e2.insert(END, 10000)
            e2.grid(column=1, row=3)
    
            lbl = Label(top, text="iMin").grid(column=0, row=4)
            e3 = Entry(top)
            e3.insert(END, self.compartments[neuro].imin)
            e3.grid(column=1, row=4)
    
            lbl = Label(top, text="iMax").grid(column=0, row=5)
            e4 = Entry(top)
            e4.insert(END, self.compartments[neuro].imax)
            e4.grid(column=1, row=5)


            b = Button(top, text="Create", command=lambda: 
                       [self.addInjection(injType.get(), getConnObject(name), e1.get(), e2.get(), e3.get(), e4.get(), e5.get()),
                        top.destroy()],width=25).grid(column=0, row=6)
            
            
        lbl = Label(window, text="Select Injection").grid(column=0, row=1)
        optMenu = OptionMenu(window, connStr, *connAvailableStr, command=changeConn).grid(column=1, row=1)

        Button(window, text="Create", command=lambda :getName(window, connStr.get()),width=25).grid(column=1, row=2)
   
        # lbl = Label(window, text="P0").grid(column=0, row=4)  
        # e1 = Entry(window)
        # e1.insert(END, self.compartments[getName(connStr.get())].agoniste)
        # e1.grid(column=1, row=4)
       
        # lbl = Label(window, text="Q0").grid(column=0, row=5)  
        # e5 = Entry(window)
        # e5.insert(END, 0)
        # e5.grid(column=1, row=5)

        # lbl = Label(window, text="TauInj").grid(column=0, row=6)
        # e2 = Entry(window)
        # e2.insert(END, 10000)
        # e2.grid(column=1, row=6)

        # lbl = Label(window, text="iMin").grid(column=0, row=5)
        # e3 = Entry(window)
        # e3.insert(END, 0.3)
        # e3.grid(column=1, row=5)

        # lbl = Label(window, text="iMax").grid(column=0, row=7)
        # e4 = Entry(window)
        # e4.insert(END, 2.5)
        # e4.grid(column=1, row=7)


        # print(e1.get())
        # print(e5.get())
        # print(e2.get())
        # print(e3.get())
        # print(e4.get())


        window.mainloop()


    #------------------------------Graph generation-----------------------------------------

    def displayGraph(self):
        dot = Digraph()
        
        for cName in self.compartments .keys():
            if cName not in self.nlist:
                dot.node(str(cName),str(cName))
        
        for c in self.compartments.keys():
            if c not in self.nlist:
                for conn in self.compartments[c].connections:
                    if conn.weight < 0:
                        dot.edge(str(conn.source.name),str(conn.target.name), constraint='true',directed='false',arrowhead='tee')
                    if conn.weight >= 0:
                        dot.edge(str(conn.source.name),str(conn.target.name), constraint='true',directed='false')

        dot.render('Network-Graph.gv', view=True)


    #------------------------------Save the results-----------------------------------------

    def getResults(self) :
        self.runSim()
        self.writeInFile(filedialog.asksaveasfile(title="Save as", initialdir=os.getcwd(), mode="w", defaultextension=".csv"),self.results)
