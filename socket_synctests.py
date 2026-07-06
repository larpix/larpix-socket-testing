# this might read in a data file and calculate and/or make plots of baseline values

import subprocess,os,sys
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
import time
import sys

mypid=os.getpid()
os.environ['PRINT_TIME_PID']=str(mypid)

print(mypid)
print('mypid in socket_baselines is ',mypid)

print(f"Arguments count: {len(sys.argv)}")
print(sys.argv)
if len(sys.argv) >= 2 : #We got some arguments passed to our python code, it should be the output dir
    DateDirPath = sys.argv[1]
    if len(sys.argv)>2 :
        BasePath = sys.argv[2]
    else:
        BasePath=''
    print("Using output dir ",DateDirPath, ' and BasePath ',BasePath)
else:
    DateDirPath = time.strftime("%y%m%d")
if not os.path.exists(BasePath+DateDirPath) : os.mkdir(BasePath+DateDirPath)

NumASICchannels = 64

max = [0] * NumASICchannels
min = [0] * NumASICchannels
mean = [0] * NumASICchannels
sdev = [0] * NumASICchannels
nentries = [0] * NumASICchannels

def getData(filename):
    d = h5py.File(filename,mode='r')
    date = list(d['_header'].attrs.values())[0]   
    d = d['packets']
    print("read ",filename," with ",len(d)," packets")
    d2 = pd.DataFrame(d[0:len(d)])
    #print(d2)
    return date,d2

def getReceiptStats(ReceiptTimes, chan):
    global max, min, mean, sdev
    nentries[chan] = len(ReceiptTimes)
    if nentries[chan] == 0 : return
    mx = np.max(ReceiptTimes)
    mn = np.min(ReceiptTimes)
    m = round(np.mean(ReceiptTimes),2)
    sd = round(np.std(ReceiptTimes),2)
    print("Chan {} Mean {} and Std {} and max {} and min {} for {} entries "
		  .format(chan,m,sd,mx,mn,nentries[chan]))
    mean[chan] = m
    sdev[chan] = sd
    max[chan] = mx
    min[chan] = mn

def TimeStampLoop(data,firstChan=0,lastChan=NumASICchannels-1):
    #print(data)
    for chan in range(firstChan,lastChan+1):
        ReceiptTimeStats(data,chan)

def ReceiptTimeStats(data,chan):
    #datachunk = getData(filename)
    tempchunk = data[data['channel_id']==chan]
    tempchunk = tempchunk['receipt_timestamp'][tempchunk['packet_type']==1] # packet type 1 for v3, 0 for <v3
    getReceiptStats(tempchunk,chan)
 
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

filename = 'testingSync.h5' # all NumASICchannels channels for 1 second

runtime, datachunk = getData(filename)

datachunk = datachunk[datachunk['packet_type']==1] # select only data packets 1 for v3, 0 for <v3

if len(datachunk)==0 : exit("No packet data in file")

# Dump raw data to csv file
datachunk.to_csv("tempSync.csv")

tempstatus = h5py.File("CurrentRun.tmp",mode='r')
dset = tempstatus['CurrentRun']
ChipSN = dset.attrs['ChipSN']
tempstatus.close()

fig = px.histogram(datachunk,x='dataword',color='channel_id',log_y=True,opacity=0.6)
fig.update_layout(barmode='overlay')
if os.getenv('socket_PlotBaselineChannels')=='1':
	fig.show()	

SyncDirPath = BasePath+DateDirPath+"/synctests/"
if not os.path.exists(SyncDirPath) : os.mkdir(SyncDirPath)

testcycle=0
maxtestcycle=100
while testcycle < maxtestcycle:
	outfile=SyncDirPath+"/Synctest_"+DateDirPath+"-"+ChipSN+"-"+str(testcycle)+".html"
	if not os.path.isfile(outfile): break
	testcycle=testcycle+1
fig.write_html(outfile,auto_open=False )

TimeStampLoop(datachunk,0,NumASICchannels-1)

# Save raw .h5 baseline data
# copy h5 file to new location to be analyzed later
testcycle=0
maxtestcycle=100
while testcycle < maxtestcycle:
	outfile=SyncDirPath+"/syncraw-"+DateDirPath+"-"+ChipSN+"-"+str(testcycle)+".h5"
	if not os.path.isfile(outfile): break
	testcycle=testcycle+1
subprocess.run(["cp","testingSync.h5",outfile])

#Output to csv files

#varlist = []

print('Processing data for chip ',ChipSN)

summaryFrame = pd.DataFrame(columns = ['runtime','MaxReceipt','MinReceipt','MeanReceipt','StdReceipt','Nent','ChanName','Chan','ChipSN'])

#fig2=go.Figure()
#for chan in range(NumASICchannels):
#	t=datachunk[datachunk['channel_id']==chan]
#	y=t['dataword']
#	x=np.arange(1,len(y))
#	print("plotting channel ",chan," with ",len(y)," samples")
#	fig2.add_trace(go.Scatter(x=x,y=y,name=str(chan)))
#fig2.write_html("channels.html")

# I should be able to add this as vectors instead of one-by-one
for chan in range(NumASICchannels): 
	textchan = 'ch{:02d}'.format(chan) 
	summaryFrame = pd.concat([summaryFrame,pd.DataFrame({'runtime':runtime,'MaxReceipt':max[chan],'MinReceipt':min[chan],'MeanReceipt':mean[chan],'StdReceipt':sdev[chan],
	'Nent':nentries[chan],'ChanName':textchan,'Chan':chan,
	'ChipSN':ChipSN},index=[0])] )

# New dated file paths and names  
summaryFile=BasePath+DateDirPath+"/receipt-summary"+DateDirPath+".csv"
# If file exists, append with no header
if os.path.exists(summaryFile) : summaryFrame.to_csv(summaryFile,mode='a',header=False)
# else create file with header
else : summaryFrame.to_csv(summaryFile,mode='a',header=True)

global nBadSyncs

if np.max(max) > 12000 :
    nBadSyncs=1
else:
    nBadSyncs=0
    print("no bad syncs found")

os.environ['socket_BadSyncs']=str(nBadSyncs)
sys.exit(nBadSyncs)

