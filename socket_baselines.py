# this might read in a data file and calculate and/or make plots of baseline values

import os
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
if len(datachunk)==0 : exit("No packet data in file")
#print(datachunk)
io_group=datachunk['io_group'].iloc[0]
io_channel=datachunk['io_channel'].iloc[0]
#print('data from io_group: ',io_group,' and io_channel: ',io_channel)
#datachunk.shape
#id(datachunk)

#datachunk.to_csv("temp.csv")

# grab user input for barcode SN

#ChipSN = mychipIDBox[0].get()
tempstatus = h5py.File("CurrentRun.tmp",mode='r')
dset = tempstatus['CurrentRun']
ChipSN = dset.attrs['ChipSN']
tempstatus.close()

fig = px.histogram(datachunk,x='dataword',color='channel_id',log_y=True,opacity=0.6)
fig.update_layout(barmode='overlay')
fig.show()	

plotly.offline.plot(fig,filename="baselines/Baseline_"+ChipSN+".html",auto_open=False )

BaselineLoop(datachunk,0,NumASICchannels-1)

#Output to csv files

#varlist = []

print('Processing data for chip ',ChipSN)

#tray = input("Enter the tray number: ")
#tRow = input("Enter the row number 0=bottom 14=top: ")
#tColumn = input("Enter the column number 0=left 5=right: ")

#summaryFrame = pd.DataFrame(columns = ['runtime','Mean','Std','Nent','ChanName','Chan','Tray','tRow','tColumn'])
summaryFrame = pd.DataFrame(columns = ['runtime','Mean','Std','Nent','ChanName','Chan','ChipSN','io_group','io_channel'])

for chan in range(NumASICchannels): 
	textchan = 'ch{:02d}'.format(chan) 
	summaryFrame = summaryFrame.append({'runtime':runtime,'Mean':mean[chan],'Std':sdev[chan],
	'Nent':nentries[chan],'ChanName':textchan,'Chan':chan,
	'ChipSN':ChipSN,'io_group':io_group,'io_channel':io_channel},ignore_index=True)


#summaryFrame.to_csv("t.csv",mode='a',header=True)
summaryFrame.to_csv("t.csv",mode='a',header=False)

# Load limits dataFrame Should do this from a file at some point.

MeanMeanbyChan=[14.07, 14.2, 14.27, 14.6, 15.34, 15.54, -999.0, -999.0, -999.0, -999.0, 42.58, 23.44, 19.02, 14.67, 14.19, 14.11, 13.18, 14.08, 14.2, 15.68, 15.45, 16.52, -999.0, -999.0, -999.0, -999.0, 11.48, 12.02, 10.47, 10.51, 13.3, 12.35, 12.34, 14.77, 15.06, 14.7, 18.25, 21.93, -999.0, -999.0, -999.0, 9.6, 11.35, 11.72, 9.15, 11.74, 11.8, 9.56, 12.02, 11.94, 9.9, 11.82, 11.92, 11.35, -999.0, -999.0, -999.0, -999.0, 12.2, 12.88, 12.98, 13.31, 13.55, 13.64]
StdMeanbyChan=[1.69, 1.87, 1.98, 11.15, 1.96, 2.21, -999.0, -999.0, -999.0, -999.0, 2.59, 2.6, 2.14, 1.88, 1.79, 1.75, 1.79, 1.82, 1.78, 2.06, 8.48, 2.53, -999.0, -999.0, -999.0, -999.0, 1.7, 1.8, 1.68, 1.83, 1.76, 1.89, 1.59, 1.84, 1.77, 1.62, 1.54, 1.92, -999.0, -999.0, -999.0, 1.69, 1.65, 1.69, 1.79, 1.68, 1.7, 1.65, 1.65, 1.7, 1.66, 1.82, 1.72, 1.85, -999.0, -999.0, -999.0, -999.0, 7.76, 2.06, 1.8, 1.89, 1.65, 1.94]
MeanStdbyChan=[1.36, 1.4, 1.46, 1.58, 1.9, 5.14, -999.0, -999.0, -999.0, -999.0, 3.71, 2.68, 2.31, 2.16, 2.18, 2.28, 2.45, 2.71, 3.16, 3.92, 4.86, 7.96, -999.0, -999.0, -999.0, -999.0, 2.26, 2.03, 2.11, 1.95, 1.65, 1.87, 1.83, 1.64, 1.99, 2.18, 2.39, 3.75, -999.0, -999.0, -999.0, 3.72, 2.47, 1.72, 1.64, 1.44, 1.37, 1.53, 1.37, 1.39, 1.61, 1.55, 1.65, 1.99, -999.0, -999.0, -999.0, -999.0, 1.37, 1.35, 1.35, 1.33, 1.32, 1.34]
StdStdbyChan=[1.46, 4.34, 2.88, 2.83, 2.49, 2.45, -999.0, -999.0, -999.0, -999.0, 1.71, 4.55, 3.47, 2.85, 3.21, 3.17, 2.87, 3.44, 3.85, 3.71, 3.26, 4.39, -999.0, -999.0, -999.0, -999.0, 1.74, 1.88, 2.98, 2.74, 1.7, 2.6, 2.61, 1.66, 2.61, 2.77, 1.56, 1.43, -999.0, -999.0, -999.0, 1.87, 1.69, 1.6, 2.6, 1.49, 1.47, 2.77, 1.52, 1.88, 2.72, 1.38, 1.74, 2.19, -999.0, -999.0, -999.0, -999.0, 1.79, 1.65, 1.49, 1.86, 2.81, 4.21]

limitsdf=pd.DataFrame(columns=['Mean','errMean','Std','errStd','ChanName','Chan'])

for chan in range(NumASICchannels):
	#if MeanMeanbyChan[chan]!=-999.:
	textchan = 'ch{:02d}'.format(chan)
	#original 38 used these
	#errMean=3 * max(StdMeanbyChan[chan],4.0)
	#errStd=5 * max(StdStdbyChan[chan],0.7)
	errMean=1.0 * max(StdMeanbyChan[chan],10.0)
	errStd=1.0 * max(StdStdbyChan[chan],3.0)
	limitsdf=limitsdf.append({'Mean':MeanMeanbyChan[chan],'errMean':errMean,'Std':MeanStdbyChan[chan],
	'errStd':errStd,'ChanName':textchan,'Chan':chan},ignore_index=True)

# END Loading limits dataFrame

AllbadChan = summaryFrame[ (summaryFrame['Chan']==64) ] # gets an empty dataFrame
for chan in range(NumASICchannels):
	#if MeanMeanbyChan[chan]!=-999:
	if limitsdf['Mean'][limitsdf['Chan']==chan].values[0]!=-999.: # :MeanMeanbyChan[chan]!=-999:
		theMean=limitsdf['Mean'][(limitsdf['Chan']==chan)].values[0]
		theStd=limitsdf['Std'][(limitsdf['Chan']==chan)].values[0]
		theErrMean=limitsdf['errMean'][(limitsdf['Chan']==chan)].values[0]
		theErrStd=limitsdf['errStd'][(limitsdf['Chan']==chan)].values[0]
		MaxMean = round(theMean + 1.0 * max(theErrMean,10.0),2)
		MinMean = round(theMean - 1.0 * max(theErrMean,10.0),2)
		MaxStd = round(theStd + 1.0 * max(theErrStd,3.0),2)
		MinStd = round(theStd - 1.0 * max(theErrStd,3.0),2)
		#print('Range for chan ',chan,' Mean and Std= [',MinMean,',',MaxMean,'][',MinStd,',',MaxStd,']')
		#badChan =summaryFrame[ (summaryFrame['Chan']==chan) & ((summaryFrame['Std']<1) | (summaryFrame['Mean']>240)) ]
		badChan =summaryFrame[ (summaryFrame['Chan']==chan) & ( ( (summaryFrame['Std']>MaxStd) | (summaryFrame['Std']<MinStd) )
				| ( (summaryFrame['Mean']<MinMean) | (summaryFrame['Mean']>MaxMean) ) ) ]
		if badChan.empty==False: 
			print(badChan)
			print('Range for chan ',chan,' Mean and Std= [',MinMean,',',MaxMean,'][',MinStd,',',MaxStd,']')
		#AllbadChan.append(badChan,ignore_index=True)
		AllbadChan=pd.concat([AllbadChan,badChan],ignore_index=True)
global nBadBaselineChannels
if AllbadChan.empty==True:
	print("No bad Channels found")
	nBadBaselineChannels=0
else:
	print(AllbadChan)
	nBadBaselineChannels=len(AllbadChan)

os.environ['socket_BadBaselineChannels']=str(nBadBaselineChannels)


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

