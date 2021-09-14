
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

#varlist = []
#for chan in range(0,32): varlist.append('ch{:02d}'.format(chan))

#meandf = pd.read_csv("20200131_all78/means.csv")
#stddf = pd.read_csv("20200131_all78/sdevs.csv")
#nentdf = pd.read_csv("20200131_all78/nents.csv")
#meandf.plot.hist()
#fig = px.histogram(sdev)
#fig = px.histogram(stddf)
#fig.show()
#fig = px.histogram(stddf,x='ch00')
#fig.show()
#fig = px.histogram(meandf,x='ch00')
#fig.show()

#fig4 = go.Figure()
#for graph in varlist: fig4.add_trace(go.Histogram(x=nentdf[graph]))

#fig4.show()

#fig5 = px.scatter(x=meandf[],y=stddf[])
#fig3.update_layout(barmode="stack")
#fig3.update_layout(barmode="overlay")
#for graph in varlist: fig3.add_trace(go.Histogram(x=meandf[graph],xbins=dict(start=0,end=255,size=3)))

#fig3.show()

# reshape separate csvs to single summary.csv

#summaryFrame = pd.DataFrame(columns = ['runtime','Mean','Std','Nent','ChanName','Chan'])
#summaryFrame2 = pd.read_csv("20200204_tray1_summary.csv")
#summaryFrame = pd.read_csv("20200131_all78/summary.csv")
#summaryFrame = pd.read_csv("20200204_tray0_summary.csv")
#summaryFrame = pd.read_csv("20200206_boiling_pixel.csv")

# BATCH 1
BATCH1=False
#BATCH1=True
if BATCH1:
	summaryFrame = pd.read_csv("20200826_v2First38.csv")
	summaryFrame = summaryFrame.append(pd.read_csv("20200829_2540-2629.csv"),ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20200830_2450-2539.csv"),ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20200828_2630-2719.csv"),ignore_index=True)

# BATCH 2
BATCH2=False
#BATCH2=True
if BATCH2:
	summaryFrame = summaryFrame.append(pd.read_csv("20200922_2449-2258.csv"),ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20200925_2257-2090.csv"),ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20200925_2089-1987.csv"),ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20200926_1986-1940.csv"),ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20200928_1939-1843.csv"),ignore_index=True)
BATCH2Part2=False
#BATCH2Part2=True
if BATCH2Part2:
	summaryFrame = summaryFrame.append(pd.read_csv("20201002_1843-1820.csv"),ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20201003_1819-1730.csv"),ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20201004_1729-1640.csv"),ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20201007_1639-1548.csv"),ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20201015_1547-1440.csv"),ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20201015_1439-1335.csv"),ignore_index=True)	
	summaryFrame = summaryFrame.append(pd.read_csv("20201016_1334-1266.csv"),ignore_index=True)	
	summaryFrame = summaryFrame.append(pd.read_csv("20201018_1265-1190.csv"),ignore_index=True)	
	summaryFrame = summaryFrame.append(pd.read_csv("20201018_1189-1134.csv"),ignore_index=True)	
	summaryFrame = summaryFrame.append(pd.read_csv("20201019_1133-1100.csv"),ignore_index=True)

# Compare brd3 vs brd4
brd3vbrd4=False
if brd3vbrd4:
	summaryFrame = pd.read_csv("20201002_brd3_brd4.csv") # insertion on each test

# Compare brd3 vs brd4
brdl3vbrdp5=False
if brdl3vbrdp5:
	summaryFrame = pd.read_csv("20201013_brdl3-brdp5.csv") # insertion on each test

BATCH3Part2=False
#BATCH3Part2=True
if BATCH3Part2:
	#summaryFrame = pd.read_csv("20201022_1099-1010.csv",dtype={'ChipSN':'string'})
	summaryFrame = summaryFrame.append(pd.read_csv("20201022_1099-1010.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20201022_1009-0921.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20201026_0919-0854.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20201027_0853-0728.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20201028_0727-0668.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20201029_0667-0578.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20201030_0577-0434.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20201031_0433-0337.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20201101_0336-0258.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20201101_0257-0200.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)

# Pkg BATCH 2
PkgBATCH2=False
PkgBATCH2=True
if PkgBATCH2:
	summaryFrame = pd.read_csv("20210401_3089-3000.csv")
	summaryFrame = summaryFrame.append(pd.read_csv("20210406_3198-3090.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20210408_3406-3199.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20210414_3490-3407.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20210414_3629-3491.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20210414_3767-3630.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20210414_3899-3768.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)
	summaryFrame = summaryFrame.append(pd.read_csv("20210414_3989-3900.csv",dtype={'ChipSN':'string'})
			,ignore_index=True)


#tempFrm=summaryFrame[summaryFrame['Chan']==0].to_csv("concat_data.csv",mode='w')

# adjust second set to have runtimes after the first + 60 seconds
#lasttime=summaryFrame['runtime'][len(summaryFrame.runtime)-1]
#lasttime
#firsttime2=summaryFrame2['runtime'][0]
#firsttime2
#summaryFrame2.runtime=summaryFrame2.runtime-firsttime2+lasttime+60  
#summaryFrame = summaryFrame.append(summaryFrame2,ignore_index=True)
#numrows = len(meandf['ch00'])
#for row in range(0,numrows):
#	for chan in range(0,32):
#		textchan = 'ch{:02d}'.format(chan) 
#		summaryFrame = summaryFrame.append({'runtime':meandf['runtime'][row],'Mean':meandf[textchan][row],'Std':stddf[textchan][row],'Nent':nentdf[textchan][row],'ChanName':textchan,'Chan':chan},ignore_index=True)

#mydf = pd.concat([pd.DataFrame([meandf['runtime'][row],meandf[textchan][row],stddf[textchan][row],nentdf[textchan][row],textchan,chan],columns = ['runtime','Mean','Std','Nent','ChanName','Chan']) for chan in range(32)],ignore_index=True)

#fig2 = go.Figure()
#for graph in varlist: fig2.add_trace(go.Histogram(x=stddf[graph],xbins=dict(start=0,end=255,size=1)))

#summaryFrame['ShortSN']=summaryFrame['ChipSN'].str.partition('0E')[2]
#print(summaryFrame)
# try to get ShortSN from the sequence without
#exit()
summaryFrame['ShortSN']=summaryFrame['ChipSN'].str[2:] # should get from 2 to the end, skip 0 and 1 item

MeanMeanbyChan=[]
StdMeanbyChan=[]
MeanStdbyChan=[]
StdStdbyChan=[]

# standards from first 38, used for first 307 for module 0
#MeanMeanbyChan = [14.16, 14.23, 14.34, 14.44, 15.03, 15.83, -999., -999., -999., -999., 42.28, 22.95, 18.71, 14.53, 13.69, 14.06, 13.11, 14.02, 13.97, 15.42, 15.29, 16.25, -999., -999., -999., -999., 11.38, 11.91, 10.03, 9.92, 12.54, 11.96, 11.84, 14.35, 15.0, 14.16, 18.39, 21.74, -999., -999., -999., 9.03, 11.3, 11.37, 9.08, 11.57, 11.44, 8.96, 11.83, 11.7, 9.76, 11.25, 12.06, 11.47, -999., -999., -999., -999., 12.24, 12.7, 13.19, 12.44, 13.47, 13.59]

#StdMeanbyChan = [1.39, 1.44, 1.49, 1.8, 2.05, 5.58, -999., -999., -999., -999., 3.74, 2.7, 2.34, 2.19, 2.21, 2.29, 2.52, 2.68, 3.22, 4.1, 5.13, 8.02, -999., -999., -999., -999., 2.27, 2.06, 2.14, 2.04, 1.66, 1.91, 1.86, 1.64, 2.02, 2.19, 2.43, 3.78, -999., -999., -999., 3.73, 2.52, 1.74, 1.85, 1.47, 1.41, 1.58, 1.49, 1.43, 1.69, 1.74, 2.29, 2.73, -999., -999., -999., -999., 1.55, 1.42, 1.49, 1.34, 1.35, 1.36]

#MeanStdbyChan = [1.68, 1.28, 1.91, 1.85, 1.6, 2.61, -999., -999., -999., -999., 2.54, 1.79, 1.71, 1.81, 1.82, 1.92, 1.77, 1.44, 1.97, 1.77, 1.62, 1.9, -999., -999., -999., -999., 1.96, 1.25, 1.51, 1.6, 1.72, 1.67, 1.61, 1.51, 2.06, 1.49, 1.53, 2.17, -999., -999., -999., 1.46, 1.58, 1.13, 1.88, 1.94, 2.04, 1.13, 1.64, 1.71, 1.84, 1.63, 1.88, 2.94, -999., -999., -999., -999., 1.78, 1.97, 2.02, 1.82, 1.69, 1.39]

#StdStdbyChan = [0.06, 0.05, 0.09, 0.95, 0.44, 1.69, -999., -999., -999., -999., 0.2, 0.11, 0.11, 0.13, 0.12, 0.18, 0.25, 0.28, 0.34, 0.53, 0.69, 1.3, -999., -999., -999., -999., 0.36, 0.19, 0.17, 0.3, 0.1, 0.11, 0.09, 0.08, 0.08, 0.09, 0.11, 0.16, -999., -999., -999., 0.14, 0.11, 0.07, 0.95, 0.07, 0.06, 0.09, 0.5, 0.14, 0.4, 0.96, 3.62, 4.14, -999., -999., -999., -999., 1.07, 0.35, 0.74, 0.06, 0.06, 0.05]

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

#print(limitsdf)
#fig1.show()
#plotly.offline.plot(fig5,filename="LimitsStdvsMean.html",auto_open=False )

#exit()

CalculateNewMeansAndStd=0
if CalculateNewMeansAndStd:
	MeanMeanbyChan=[]
	StdMeanbyChan=[]
	MeanStdbyChan=[]
	StdStdbyChan=[]
	# Clean the data
	summaryFrame=summaryFrame[(summaryFrame['Mean']<250) & (summaryFrame['Std']>0.1)]
	#Calculate mean for Series
	summaryFrame=summaryFrame[summaryFrame['ShortSN']!='2722'][summaryFrame['ShortSN']!='2727'][summaryFrame['ShortSN']!='2749']
	print('summaryFrame has',len(summaryFrame) ,' entries')
	for chan in range(NumASICchannels):
		#tempSeries=summaryFrame['Mean'][summaryFrame['Chan']==chan]
		#MeanbyChan.append(tempSeries.mean())
		#MeanMeanbyChan.append(round(summaryFrame['Mean'][summaryFrame['Chan']==chan].mean(),2))
		MeanMeanbyChan.append(round(summaryFrame['Mean'][summaryFrame['Chan']==chan].median(),2))
		StdMeanbyChan.append(round(summaryFrame['Mean'][summaryFrame['Chan']==chan].std(),2))
		#MeanStdbyChan.append(round(summaryFrame['Std'][summaryFrame['Chan']==chan].mean(),2))
		MeanStdbyChan.append(round(summaryFrame['Std'][summaryFrame['Chan']==chan].median(),2))
		StdStdbyChan.append(round(summaryFrame['Std'][summaryFrame['Chan']==chan].std(),2))
		print('MeanMean +- StdMean for Chan:',chan,MeanMeanbyChan[chan],'+-',StdMeanbyChan[chan])
		print('MeanStd +- StdStd for Chan:',chan,MeanStdbyChan[chan],'+-',StdStdbyChan[chan])

	print(MeanMeanbyChan)
	print(StdMeanbyChan)
	print(MeanStdbyChan)
	print(StdStdbyChan)
	exit()

fig2 = px.histogram(x=summaryFrame['Mean'],color=summaryFrame['ChanName'])
fig2.update_layout(barmode="stack",xaxis_title="Baseline Mean (ADC)")
fig2.show()
plotly.offline.plot(fig2,filename="Meanstack_bp.html",auto_open=False )

fig3 = px.histogram(x=summaryFrame['Std'],color=summaryFrame['ChanName'])
fig3.update_layout(barmode="stack",xaxis_title="Std Deviation (ADC)")
fig3.show()
plotly.offline.plot(fig3,filename="Stdstack_bp.html",auto_open=False )

fig5 = px.scatter(x=summaryFrame['Mean'],y=summaryFrame['Std'],color=summaryFrame['ChanName'])
fig5.update_layout(xaxis_title="Baseline Mean (ADC)",yaxis_title="Std Dev (ADC)")
fig5.show()
plotly.offline.plot(fig5,filename="StdvsMean_bp.html",auto_open=False )

fig1 = go.Figure()

for chan in range(NumASICchannels): #[0,1,2]:
	chanlimits=limitsdf[limitsdf['Chan']==chan]
	chanlimits.reset_index(drop=True)
	chanFrame=summaryFrame[summaryFrame['Chan']==chan]
	chanFrame.reset_index(drop=True)
	#print(chanlimits['Mean'])
	if MeanMeanbyChan[chan]>0.:
		#fig1 = px.line(x=limitsdf['Mean'],y=limitsdf['Std'],error_x=limitsdf['errMean'],error_y=limitsdf['errStd'],color=limitsdf['ChanName'])
		#fig1.add_trace(go.scatter.Line(x=limitsdf['Mean'],y=limitsdf['Std'],error_x=limitsdf['errMean'],error_y=limitsdf['errStd'])) #,color=limitsdf['ChanName']))
		fig1.add_trace(go.Scatter(name='ch{:02d}'.format(chan),
							x=chanlimits['Mean'],error_x=dict(type='data',array=chanlimits['errMean'],visible=True),
							y=chanlimits['Std'],error_y=dict(type='data',array=chanlimits['errStd'],visible=True),
								marker_color=px.colors.qualitative.Plotly[chan%10])) #,color=limitsdf['ChanName']))
		#fig1.update_layout(xaxis_title="Baseline Mean (ADC)",yaxis_title="Std Dev (ADC)")
		fig1.add_trace(go.Scatter(name='samp{:02d}'.format(chan),x=chanFrame['Mean'],y=chanFrame['Std'],mode='markers',
			marker_color=px.colors.qualitative.Plotly[chan%10])) #,color=summaryFrame['ChanName']))
fig1.show()

fig6 = px.scatter(x=summaryFrame['runtime']-summaryFrame['runtime'][0],y=summaryFrame['Std'],color=summaryFrame['ChanName'])
fig6.update_layout(xaxis_title="Run Time(s)",yaxis_title="Std Dev (ADC)")
fig6.show()
#plotly.offline.plot(fig6,filename="StdvsRuntime.html",auto_open=False )

fig7 = px.scatter(x=summaryFrame['runtime']-summaryFrame['runtime'][0],y=summaryFrame['Mean'],color=summaryFrame['ChanName'])
fig7.update_layout(xaxis_title="Run Time(s)",yaxis_title="Baseline Mean (ADC)")
fig7.show()
#plotly.offline.plot(fig7,filename="MeanvsRuntime.html",auto_open=False )

#badChan = summaryFrame[(summaryFrame['Std']<1) | (summaryFrame['Mean']>240)]
#badChan.reset_index(drop=True)
badChan = summaryFrame[ (summaryFrame['Chan']==64) ]
AllbadChan = summaryFrame[ (summaryFrame['Chan']==64) ]
print(badChan)

#pd.concat([pd.DataFrame([i], columns=['A']) for i in range(5)],ignore_index=True)
for chan in range(NumASICchannels):
	if MeanMeanbyChan[chan]!=-999:
		#	badChan = badChan + summaryFrame[ (summaryFrame['Chan']==chan) & ((summaryFrame['Std']<1) | (summaryFrame['Mean']>240)) ]
		#first versions, based on the 38
		#MaxMean = round(MeanMeanbyChan[chan] + 3 * max(StdMeanbyChan[chan],4.0),2)
		#MinMean = round(MeanMeanbyChan[chan] - 3 * max(StdMeanbyChan[chan],4.0),2)
		#MaxStd = round(MeanStdbyChan[chan] + 5 * max(StdStdbyChan[chan],0.7),2)
		#MinStd = round(MeanStdbyChan[chan] - 5 * max(StdStdbyChan[chan],0.7),2)
		theMean=limitsdf['Mean'][(limitsdf['Chan']==chan)].values[0]
		theStd=limitsdf['Std'][(limitsdf['Chan']==chan)].values[0]
		theErrMean=limitsdf['errMean'][(limitsdf['Chan']==chan)].values[0]
		theErrStd=limitsdf['errStd'][(limitsdf['Chan']==chan)].values[0]
		MaxMean = round(theMean + 1.0 * max(theErrMean,10.0),2)
		MinMean = round(theMean - 1.0 * max(theErrMean,10.0),2)
		MaxStd = round(theStd + 1.0 * max(theErrStd,3.0),2)
		MinStd = round(theStd - 1.0 * max(theErrStd,3.0),2)
		print('Range for chan ',chan,' Mean and Std= [',MinMean,',',MaxMean,'][',MinStd,',',MaxStd,']')
		#badChan =summaryFrame[ (summaryFrame['Chan']==chan) & ((summaryFrame['Std']<1) | (summaryFrame['Mean']>240)) ]
		badChan =summaryFrame[ (summaryFrame['Chan']==chan) & ( ( (summaryFrame['Std']>MaxStd) | (summaryFrame['Std']<MinStd) )
				| ( (summaryFrame['Mean']<MinMean) | (summaryFrame['Mean']>MaxMean) ) ) ]
		#print(badChan)
		#AllbadChan.append(badChan,ignore_index=True)
		AllbadChan=pd.concat([AllbadChan,badChan],ignore_index=True)
print(AllbadChan)
print(AllbadChan.groupby('ChipSN').count())

#fig8 = go.Figure()
#fig8.add_trace(go.Histogram(x=AllbadChan['ShortSN'],xbins=dict(size=1)))
#fig8.update_layout(xaxis_title="ChipSN",yaxis_title="Number Bad Channels")
#fig8.show()
#plotly.offline.plot(fig8,filename="BadChanvsChip_bp.html",auto_open=False )

fig8 = px.histogram(x=AllbadChan['ShortSN'],nbins=350,color=AllbadChan['ChanName'])
fig8.update_layout(barmode="stack",xaxis_title="Chip SN",yaxis_title="Bad Channels")
fig8.show()

fig81 = px.histogram(x=AllbadChan['Chan'],nbins=64)
fig81.update_layout(barmode="stack",xaxis_title="Channel",yaxis_title="Bad Channels")
fig81.show()


fig9 = px.scatter(x=summaryFrame['ShortSN'],y=summaryFrame['Std'],color=summaryFrame['ChanName'])
#fig9 = px.line(x=summaryFrame['ShortSN'],y=summaryFrame['Std'],color=summaryFrame['ChanName'])
fig9.update_layout(xaxis_title="ChipSN",yaxis_title="Std Dev (ADC)")
fig9.show()
plotly.offline.plot(fig9,filename="StdvsChip_bp.html",auto_open=False )

fig10 = px.scatter(x=summaryFrame['ShortSN'],y=summaryFrame['Mean'],color=summaryFrame['ChanName'])
#fig10 = px.line(x=summaryFrame['ShortSN'],y=summaryFrame['Mean'],color=summaryFrame['ChanName'])
fig10.update_layout(xaxis_title="ChipSN",yaxis_title="Baseline Mean (ADC)")
fig10.show()
plotly.offline.plot(fig10,filename="MeanvsChip_bp.html",auto_open=False )
