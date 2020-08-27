# this might read in a data file and calculate and/or make plots of baseline values

import pandas as pd
import h5py
import plotly
import plotly.express as px
import chart_studio
import chart_studio.plotly as py
import plotly.graph_objs as go
import csv
import numpy as np
from collections import Counter

NumASICchannels = 64

mean = [0] * NumASICchannels
sdev = [0] * NumASICchannels
nentries = [0] * NumASICchannels

def getData(filename):
    d = h5py.File(filename,mode='r')
    date = list(d['_header'].attrs.values())[0]   
    d = d['packets']
    d = pd.DataFrame(d[0:len(d)])
    return date,d

def getMeanAndStd(adc_list, chan):
    global mean, sdev
    m = round(np.mean(adc_list),2)
    sd = round(np.std(adc_list),2)
    print("Chan {} Mean {} and Std {} and max {} and min {} for {} entries".format(chan,m,sd,np.max(adc_list),np.min(adc_list),len(adc_list)))
    mean[chan] = m
    sdev[chan] = sd
    nentries[chan] = len(adc_list)

def BaselineLoop(data,firstChan=0,lastChan=NumASICchannels-1):
    for chan in range(firstChan,lastChan+1):
        BaselineMeanStd(data,chan)

def BaselineMeanStd(data,chan):
    #datachunk = getData(filename)
    tempchunk = data[data['channel_id']==chan]
    tempchunk = tempchunk['dataword'][tempchunk['packet_type']==0]
    getMeanAndStd(tempchunk,chan)

def plot_interactive(data, filename):
    '''plotting function'''
    layout = go.Layout(title='Baseline Histo',
                   xaxis_title='ADC value',
                   yaxis_title='Frequency',
                   paper_bgcolor='rgb(233,233,233)',
                   plot_bgcolor='rgba(0,0,0,0)'
                      )
    fig = go.Figure(data = [{ 'x': data[data[col].notnull()].index,
                              'y': data[data[col].notnull()][col],
                              'name': "{} - mean:{} , std:{}".format(col,mean[col],sdev[col]),
                              'mode':'lines+markers',
                              'line': dict(dash='dash')}  for col in data.columns],
                    layout = layout
                   )         
    plotly.offline.plot(fig,
                       filename=filename,
                        auto_open=False)

#filename = 'datalog_2020_01_14_16_05_16_PST_.h5'  # socket board chan 2-NumASICchannels-1
#filename = 'datalog_2020_01_15_11_55_06_PST_.h5' # 4 chip pixel board chan 0-NumASICchannels-1
#filename = 'datalog_2020_01_22_12_06_20_PST_.h5' # socket board chan 2-NumASICchannels-1 after clock modifications
#filename = 'datalog_2020_01_28_11_40_42_PST_.h5' # Boiling board - no mod's
#filename = 'datalog_2020_01_29_12_59_34_PST_.h5' # all NumASICchannels channels for 1 second
#filename = 'testing25.h5' # all NumASICchannels channels for 1 second
#filename = 'testing27.h5' # all NumASICchannels channels for 1 second
#filename = 'testing30.h5' # all NumASICchannels channels for 1 second
#filename = 'testing35.h5' # all NumASICchannels channels for 1 second
filename = 'testing.h5' # all NumASICchannels channels for 1 second

runtime, datachunk = getData(filename)
#datachunk.shape
#datachunk.to_csv("temp.csv")
#id(datachunk)
datachunk = datachunk[datachunk['packet_type']==0] # select only data packets
#datachunk.shape
#id(datachunk)

#datachunk.to_csv("temp.csv")

fig = px.histogram(datachunk,x='dataword',color='channel_id')
fig.update_layout(barmode='overlay')
fig.show()	

BaselineLoop(datachunk,0,NumASICchannels-1)

#Output to csv files

#varlist = []

# grab user input for tray, tRow and tColumn (will just use barcode at some point)

#ChipSN = mychipIDBox[0].get()
tempstatus = h5py.File("CurrentRun.tmp",mode='r')
dset = tempstatus['CurrentRun']
ChipSN = dset.attrs['ChipSN']
tempstatus.close()

print('Processing data for chip ',ChipSN)

#tray = input("Enter the tray number: ")
#tRow = input("Enter the row number 0=bottom 14=top: ")
#tColumn = input("Enter the column number 0=left 5=right: ")

#summaryFrame = pd.DataFrame(columns = ['runtime','Mean','Std','Nent','ChanName','Chan','Tray','tRow','tColumn'])
summaryFrame = pd.DataFrame(columns = ['runtime','Mean','Std','Nent','ChanName','Chan','ChipSN'])

for chan in range(NumASICchannels): 
	textchan = 'ch{:02d}'.format(chan) 
	summaryFrame = summaryFrame.append({'runtime':runtime,'Mean':mean[chan],'Std':sdev[chan],
	'Nent':nentries[chan],'ChanName':textchan,'Chan':chan,
	'ChipSN':ChipSN},ignore_index=True)


#summaryFrame.to_csv("t.csv",mode='a',header=True)
summaryFrame.to_csv("t.csv",mode='a',header=False)

#meandf = pd.DataFrame(mean)
#stddf = pd.DataFrame(sdev)
#nentdf = pd.DataFrame(nentries)

#meandf=meandf.transpose()
#stddf=stddf.transpose()
#nentdf=nentdf.transpose()

#meandf.columns = varlist
#stddf.columns = varlist
#nentdf.columns = varlist

#meandf.insert(0,'runtime',runtime)
#stddf.insert(0,'runtime',runtime)
#nentdf.insert(0,'runtime',runtime)

#meandf.columns = varlist

#meandf.to_csv("means.csv",mode='a',header=True)
#stddf.to_csv("sdevs.csv",mode='a',header=True)
#nentdf.to_csv("nents.csv",mode='a',header=True)

#meandf.to_csv("means.csv",mode='a',header=False)
#stddf.to_csv("sdevs.csv",mode='a',header=False)
#nentdf.to_csv("nents.csv",mode='a',header=False)

#meandf = pd.read_csv("20200131_all78/means.csv")
#stddf = pd.read_csv("20200131_all78/sdevs.csv")
#nentdf = pd.read_csv("20200131_all78/nents.csv")

#x = ["Apples","Apples","Apples","Oranges", "Bananas"]
#y = ["5","10","3","10","5"]

#fig2 = go.Figure()
#fig2.add_trace(go.Histogram(histfunc="count", x=sdev, nbinsx=50, name="count"))
#fig.add_trace(go.Histogram(histfunc="sum", y=y, x=x, name="sum"))

#fig2.show()

