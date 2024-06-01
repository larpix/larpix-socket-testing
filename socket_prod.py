# run from /home/apdlab/larpixv2/larpix-socket-testing
# after running env3  
# cd ~/larpixv2/ ;  source bin/activate

import subprocess,sys,os,signal
from subprocess import Popen,PIPE,CalledProcessError,STDOUT
import larpix
from larpix import Controller
#from larpix.io.zmq_io import ZMQ_IO
from larpix.io import PACMAN_IO
from larpix.logger.h5_logger import HDF5Logger
import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import h5py
import pandas as pd
import runpy
import numpy as np
import simpleaudio as sa
import tcp_server_prod as tsp
import csv
#import t
global SNList
global PacmanVersion
PacmanVersion = 'RevS1'
#PacmanVersion = 'pacman4'


SNList = []


#DumbFunc('another one')

sadSong = sa.WaveObject.from_wave_file('sounds/Sad_Trombone-Joe_Lamb-665429450.wav')
successSong = sa.WaveObject.from_wave_file('sounds/TaDaSoundBible.com-1884170640.wav')
doneSong = sa.WaveObject.from_wave_file('sounds/service-bell_daniel_simion.wav')

NumASICchannels = 64

def setv2channelmask():
	DisabledChannels = [6,7,8,9,22,23,24,25,38,39,40,54,55,56,57]
	for chan in DisabledChannels: TileChannelMask[chan]=0

TileChannelMask = [1] * NumASICchannels
#To enable only a few channels, set [0] above and list channel in EnabledChannels
# and uncomment the 2 lines below. To enable all channels do the reverse, set [1]
# and comment out the 2 lines below.
#EnabledChannels = [10,19,20,21,22,23,24,40]
#for chan in EnabledChannels: TileChannelMask[chan]=1

TileChannelMask 

#[1, 1, 1, 1, 1, 1, 0, 0,
# 0, 0, 1, 1, 1, 1, 1, 1, 
# 1, 1, 1, 1, 1, 1, 0, 0, 
# 0, 0, 1, 1, 1, 1, 1, 1,
# 1, 1, 1, 1, 1, 1, 0, 0,
# 0, 1, 1, 1, 1, 1, 1, 1,
# 1, 1, 1, 1, 1, 1, 0, 0,
# 0, 0, 1, 1, 1, 1, 1, 1]

def init_controller():
	c = Controller()
	if PacmanVersion == 'RevS1' :
	#c.io = ZMQ_IO('../configs/io/daq-srv1.json', miso_map={2:1})
		print('Intializing pacman20 RevS1')
		c.io = PACMAN_IO(config_filepath='/home/apdlab/larpixv2/configs/io/pacman20.json')
	elif PacmanVersion == 'pacman4': 
		print('Intializing pacman4 ')
		c.io = PACMAN_IO(config_filepath='/home/apdlab/larpixv2/configs/io/pacman4.json')
	else:
		exit('PacmanVersion not specified, exiting...')
	c.io.ping()
	return c

def init_board_base(c,_default_io_channel=1):
	##### setup hydra network configuration
	#if controller_config is None:
	#if PacmanVersion == 'RevS1' and v2bState.get() == '1':
	if PacmanVersion == 'RevS1' and ASICversion.get() == 'v2b':
		Tile_ID = 2
	else:  # v2a
		Tile_ID = 1
	##### default network (single chip) if no hydra network provided
	_default_io_group = 1
	_default_chip_id = 2
	_default_miso_ds = _default_io_channel -1 #0
	_default_mosi = _default_io_channel -1 #0
	_default_io_channel = 4*(Tile_ID-1) + _default_io_channel

	if ASICversion.get() == 'v2a':  
		c.add_chip(larpix.Key(_default_io_group, _default_io_channel, _default_chip_id))
	#elif v2bState.get() == '1':
	elif ASICversion.get() == 'v2b':
		c.add_chip(larpix.Key(_default_io_group, _default_io_channel, _default_chip_id),version='2b')
	c.add_network_node(_default_io_group, _default_io_channel, c.network_names, 'ext', root=True)
	c.add_network_link(_default_io_group, _default_io_channel, 'miso_us', ('ext',_default_chip_id), 0)
	c.add_network_link(_default_io_group, _default_io_channel, 'miso_ds', (_default_chip_id,'ext'),_default_miso_ds)
	c.add_network_link(_default_io_group, _default_io_channel, 'mosi', ('ext', _default_chip_id), _default_mosi)
	#else:
	#c.load(controller_config)


def measure_currents(c):
	loop=0
	looplimit=2
	while loop<looplimit :
		vddd_meas=c.io.get_vddd()
		vdda_meas=c.io.get_vdda()
		print('read vddd =',vddd_meas)
		print('read vdda =',vdda_meas)
		loop=loop+1	

def powerdown_exit(c):
	#Disable chip power and interface at end
	# Disable Tile
	c.io.disable_tile()
	#zero supply voltages
	c.io.set_vddd(0) # set vddd 0V
	c.io.set_vdda(0) # set vdda 0V
	exit()

def powerdown(c):
	#Disable chip power and interface at end
	# Disable Tile
	c.io.disable_tile()
	#zero supply voltages
	c.io.set_vddd(0) # set vddd 0V
	c.io.set_vdda(0) # set vdda 0V
	

def wait_here():
	trash=input('Hit <ENTER> key to proceed')
	

#test flipping bits in config register and see that they configure
def test_config_registers(c,chip):
	#print(chip.config)
	#invert chip config (for many registers)
	# CSA GAIN
	flipmask=0b1
	chip.config.csa_gain=flipmask^chip.config.csa_gain
	# CSA BYPASS ENABLE
	flipmask=0b1
	chip.config.csa_bypass_enable=flipmask^chip.config.csa_bypass_enable
	# BYPASS CAPS EN
	flipmask=0b1
	chip.config.bypass_caps_en=flipmask^chip.config.bypass_caps_en
	# PERIODIC RESET CYCLES
	flipmask=0xFF_FFFF
	chip.config.periodic_reset_cycles=flipmask^chip.config.periodic_reset_cycles

	for chan in range(0,NumASICchannels):

		# Pixel Trim DAC
		#print('{:05b}'.format(chip.config.pixel_trim_dac[chan]))
		#flipmask=int('11111',2)
		flipmask=0b1_1111
		chip.config.pixel_trim_dac[chan]=flipmask^chip.config.pixel_trim_dac[chan]
		#print('{:05b}'.format(chip.config.pixel_trim_dac[chan]))

		# CSA ENABLE
		flipmask=0b1
		chip.config.csa_enable[chan]=flipmask^chip.config.csa_enable[chan]

		# CSA BYPASS SELECT
		flipmask=0b1
		chip.config.csa_bypass_select[chan]=flipmask^chip.config.csa_bypass_select[chan]

		# CSA MONITOR SELECT
		flipmask=0b1
		chip.config.csa_monitor_select[chan]=flipmask^chip.config.csa_monitor_select[chan]

		# CSA TESTPULSE ENABLE
		flipmask=0b1
		chip.config.csa_testpulse_enable[chan]=flipmask^chip.config.csa_testpulse_enable[chan]

		# CHANNEL MASK
		flipmask=0b1
		chip.config.channel_mask[chan]=flipmask^chip.config.channel_mask[chan]

		# EXTERNAL TRIGGER MASK
		flipmask=0b1
		chip.config.external_trigger_mask[chan]=flipmask^chip.config.external_trigger_mask[chan]

		# CROSS TRIGGER MASK
		flipmask=0b1
		chip.config.cross_trigger_mask[chan]=flipmask^chip.config.cross_trigger_mask[chan]

		# PERIODIC TRIGGER MASK
		flipmask=0b1
		chip.config.periodic_trigger_mask[chan]=flipmask^chip.config.periodic_trigger_mask[chan]

	#print(chip.config)
	#exit()

	c.write_configuration(chip.chip_key)
	verified,returnregisters=c.verify_configuration(chip.chip_key,n=2)
	#print(verified)
	if verified == False : # try again
		print(returnregisters)
		verified,returnregisters=c.verify_configuration(chip.chip_key,n=2)

	if verified == False : # exit
		#Disable chip power and interface at end
		print("Verify config failed with flipped config")
		#powerdown(c)
		return 2

	#invert chip config (for many registers) (returns to original)
	# CSA GAIN
	flipmask=0b1
	chip.config.csa_gain=flipmask^chip.config.csa_gain
	# CSA BYPASS ENABLE
	flipmask=0b1
	chip.config.csa_bypass_enable=flipmask^chip.config.csa_bypass_enable
	# BYPASS CAPS EN
	flipmask=0b1
	chip.config.bypass_caps_en=flipmask^chip.config.bypass_caps_en
	# PERIODIC RESET CYCLES
	flipmask=0xFF_FFFF
	chip.config.periodic_reset_cycles=flipmask^chip.config.periodic_reset_cycles

	for chan in range(0,NumASICchannels):

		# Pixel Trim DAC
		#print('{:05b}'.format(chip.config.pixel_trim_dac[chan]))
		#flipmask=int('11111',2)		
		flipmask=0b1_1111
		chip.config.pixel_trim_dac[chan]=flipmask^chip.config.pixel_trim_dac[chan]
		#print('{:05b}'.format(chip.config.pixel_trim_dac[chan]))

		# CSA ENABLE
		flipmask=0b1
		chip.config.csa_enable[chan]=flipmask^chip.config.csa_enable[chan]

		# CSA BYPASS SELECT
		flipmask=0b1
		chip.config.csa_bypass_select[chan]=flipmask^chip.config.csa_bypass_select[chan]

		# CSA MONITOR SELECT
		flipmask=0b1
		chip.config.csa_monitor_select[chan]=flipmask^chip.config.csa_monitor_select[chan]

		# CSA TESTPULSE ENABLE
		flipmask=0b1
		chip.config.csa_testpulse_enable[chan]=flipmask^chip.config.csa_testpulse_enable[chan]

		# CHANNEL MASK
		flipmask=0b1
		chip.config.channel_mask[chan]=flipmask^chip.config.channel_mask[chan]

		# EXTERNAL TRIGGER MASK
		flipmask=0b1
		chip.config.external_trigger_mask[chan]=flipmask^chip.config.external_trigger_mask[chan]

		# CROSS TRIGGER MASK
		flipmask=0b1
		chip.config.cross_trigger_mask[chan]=flipmask^chip.config.cross_trigger_mask[chan]

		# PERIODIC TRIGGER MASK
		flipmask=0b1
		chip.config.periodic_trigger_mask[chan]=flipmask^chip.config.periodic_trigger_mask[chan]

	c.write_configuration(chip.chip_key)
	# Global Threshold Has to be done when channels already masked off or floods the controller.
	flipmask=0xFF
	chip.config.threshold_global=flipmask^chip.config.threshold_global
	c.write_configuration(chip.chip_key)
	verified,returnregisters=c.verify_configuration(chip.chip_key,n=2)
	#print(verified)
	if verified == False : # try again
		print(returnregisters)
		verified,returnregisters=c.verify_configuration(chip.chip_key,n=2)

	if verified == False : # exit
		#Disable chip power and interface at end
		print("Verify config failed with restored config")
		#powerdown(c)
		return 1

	# Global Threshold
	flipmask=0xFF
	chip.config.threshold_global=flipmask^chip.config.threshold_global

	print("config with flipped bits succeeded")
	return 0

def conf_root(c,cm,cadd,iog,iochan):
	I_TX_DIFF=0
	TX_SLICE=15
	R_TERM=2
	I_RX=8
	#REF_CURRENT_TRIM = 0
	REF_CURRENT_TRIM = 15
	if ASICversion.get() == 'v2b':
		CurrentASIC='2b'
	elif ASICversion.get() == 'v2c':
		CurrentASIC='2b'  # yes, 2b, apparently 2c never implemented, and not different
	elif ASICversion.get() == 'v2d':
		CurrentASIC='2d'
	else:
		print('Unknown ASIC version: ',ASICversion.get())
		return
	c.add_chip(cm,version=CurrentASIC)
	#  - - default larpix chip_id is '1'
	default_key = larpix.key.Key(iog, iochan, 1) # '1-5-1'
	c.add_chip(default_key,version=CurrentASIC) # was hardcoded to '2b'
	#  - - rename to chip_id = cm
	c[default_key].config.chip_id = cadd
	c.write_configuration(default_key,'chip_id')
	#  - - remove default chip id from the controller
	c.remove_chip(default_key)
	#  - - and add the new chip id
	#print('cm = ',cm)

	c[cm].config.chip_id=cadd

	c[cm].config.i_rx0=I_RX
	c.write_configuration(cm, 'i_rx0')
	c[cm].config.r_term0=R_TERM
	c.write_configuration(cm, 'r_term0')

	c[cm].config.i_rx1=I_RX
	c.write_configuration(cm, 'i_rx1')
	c[cm].config.r_term1=R_TERM
	c.write_configuration(cm, 'r_term1')

	c[cm].config.i_rx2=I_RX
	c.write_configuration(cm, 'i_rx2')
	c[cm].config.r_term2=R_TERM
	c.write_configuration(cm, 'r_term2')

	c[cm].config.i_rx3=I_RX
	c.write_configuration(cm, 'i_rx3')
	c[cm].config.r_term3=R_TERM
	c.write_configuration(cm, 'r_term3')
	#c[cm].config.enable_posi=[1,1,1,1] # all
	if iochan%4 == 1:  
		c[cm].config.enable_posi=[1,0,0,0] # posi1 ds for probe 
	elif iochan%4 == 2:
		c[cm].config.enable_posi=[0,1,0,0] # posi2 ds for probe 
	elif iochan%4 ==3:
		c[cm].config.enable_posi=[0,0,1,0] # posi3 ds for probe 
	elif iochan%4 ==0:
		c[cm].config.enable_posi=[0,0,0,1] # posi4 ds for probe 
	else :
		print('confused by iochan ',iochan)
	#c[cm].config.enable_posi=[1,0,0,0] # posi 1
	#c[cm].config.enable_posi=[0,1,0,0] # posi 2
	#c[cm].config.enable_posi=[0,0,1,0] # posi 3
	#c[cm].config.enable_posi=[0,0,0,1] # posi 4
	c.write_configuration(cm, 'enable_posi')
	c[cm].config.enable_piso_upstream=[0,0,0,0]
	c.write_configuration(cm, 'enable_piso_upstream')
	c[cm].config.i_tx_diff0=I_TX_DIFF
	c.write_configuration(cm, 'i_tx_diff0')
	c[cm].config.tx_slices0=TX_SLICE
	c.write_configuration(cm, 'tx_slices0')
	c[cm].config.i_tx_diff2=I_TX_DIFF
	c.write_configuration(cm, 'i_tx_diff2')
	c[cm].config.tx_slices2=TX_SLICE
	c.write_configuration(cm, 'tx_slices2')
	c[cm].config.i_tx_diff3=I_TX_DIFF
	c.write_configuration(cm, 'i_tx_diff3')
	c[cm].config.tx_slices3=TX_SLICE
	c.write_configuration(cm, 'tx_slices3')
	c[cm].config.i_tx_diff1=I_TX_DIFF
	c.write_configuration(cm, 'i_tx_diff1')
	c[cm].config.tx_slices1=TX_SLICE
	c.write_configuration(cm, 'tx_slices1')
	#c.io.set_reg(0x18, 1, io_group=1)
	c[cm].config.enable_piso_downstream=[1,1,1,1] # krw adding May 8, 2023
	c.write_configuration(cm, 'enable_piso_downstream')
	time.sleep(0.1)
	#c[cm].config.enable_piso_downstream=[1,0,0,1] # piso1 ds for probe
	if iochan%4 == 1:  
		c[cm].config.enable_piso_downstream=[1,0,0,0] # piso1 ds for probe 
	elif iochan%4 == 2:
		c[cm].config.enable_piso_downstream=[0,1,0,0] # piso2 ds for probe 
	elif iochan%4 ==3:
		c[cm].config.enable_piso_downstream=[0,0,1,0] # piso3 ds for probe 
	elif iochan%4 ==0:
		c[cm].config.enable_piso_downstream=[0,0,0,1] # piso4 ds for probe 
	else :
		print('confused by iochan ',iochan)
	c.write_configuration(cm, 'enable_piso_downstream')
	time.sleep(0.1)
	# enable pacman uart receiver
	rx_en = c.io.get_reg(0x18, iog)
	ch_set=pow(2,iochan-1)
	#ch_set=15
	print('enable pacman uart receiver', rx_en, ch_set, rx_en|ch_set)
	c.io.set_reg(0x18, rx_en|ch_set, iog)
	#rx_en = c.io.get_reg(0x18, iog)
	#print('rx_en ',rx_en)

	#print('c.chips')
	#print(c.chips)

def init_chips_v2c(c,io_channel):
	###########################################
	IO_GROUP = 1
	PACMAN_TILE = 2  # Assuming Pacman RevS1 (uses tile 2 for v2b,v2c and tile 1 for v2a)
	IO_CHAN = (io_channel+(PACMAN_TILE-1)*4)
	#VDDA_DAC= 44500 # ~1.8 V
	#VDDD_DAC = 28500 # ~1.1 V
	VDDA_DAC = 44500
	VDDD_DAC = 30000
	RESET_CYCLES = 300000 #5000000

	REF_CURRENT_TRIM=0
	###########################################

	# create a larpix controller
	# Already done in init_controller()
	#c = larpix.Controller()
	#c.io = larpix.io.PACMAN_IO(config_filepath='/home/apdlab/larpixv2/configs/io/pacman20.json', relaxed=True)
	io_group=IO_GROUP
	chip_id=2

	do_power_cycle = True

	if do_power_cycle:
		#disable pacman rx uarts
		#print('enable pacman power')
		bitstring = list('00000000000000000000000000000000')
		#print(int("".join(bitstring),2))
		c.io.set_reg(0x18, int("".join(bitstring),2), io_group)
		# disable tile power, LARPIX clock
		c.io.set_reg(0x00000010, 0, io_group)
		# set up mclk in pacman
		c.io.set_reg(0x101c, 0x4, io_group)
		
		# enable pacman power
		c.io.set_reg(0x00000014, 1, io_group)
		#set voltage dacs to 0V  
		c.io.set_reg(0x24010+(PACMAN_TILE-1), 0, io_group)
		c.io.set_reg(0x24020+(PACMAN_TILE-1), 0, io_group)
		#time.sleep(0.1)
		time.sleep(1)
		#set voltage dacs  VDDD first 
		c.io.set_reg(0x24020+(PACMAN_TILE-1), VDDD_DAC, io_group)
		c.io.set_reg(0x24010+(PACMAN_TILE-1), VDDA_DAC, io_group)
		

		#print('reset the larpix for n cycles',RESET_CYCLES)
		#   - set reset cycles
		c.io.set_reg(0x1014,RESET_CYCLES,io_group=IO_GROUP)
		#   - toggle reset bit
		clk_ctrl = c.io.get_reg(0x1010, io_group=IO_GROUP)
		c.io.set_reg(0x1010, clk_ctrl|4, io_group=IO_GROUP)
		c.io.set_reg(0x1010, clk_ctrl, io_group=IO_GROUP)
		
		#enable tile power
		tile_enable_val=pow(2,PACMAN_TILE-1)+0x0200  #enable one tile at a time	
		c.io.set_reg(0x00000010,tile_enable_val,io_group)
		time.sleep(0.03)
		#print('enable tilereg 0x10 , ', tile_enable_val)
		#readback=pacman_base.power_readback(c.io, io_group, pacman_version,pacman_tile)

		#   - toggle reset bit
		RESET_CYCLES = 50000
		c.io.set_reg(0x1014,RESET_CYCLES,io_group=IO_GROUP)
		clk_ctrl = c.io.get_reg(0x1010, io_group=IO_GROUP)
		c.io.set_reg(0x1010, clk_ctrl|4, io_group=IO_GROUP)
		c.io.set_reg(0x1010, clk_ctrl, io_group=IO_GROUP)
		time.sleep(0.01)

	chip_key=larpix.key.Key(IO_GROUP,IO_CHAN,chip_id)  # ASIC vsn deal with in conf_root
	conf_root(c,chip_key,chip_id,IO_GROUP,IO_CHAN)	
	c.write_configuration(chip_key)
	#verified,returnregisters=c.verify_configuration(chip_key)
	#print(verified,returnregisters)
	# Try write/read once only
	PassedConfigAt=0
	ok, diff = c.verify_configuration(chip_key, n=1 )
	# Try readback twice, only write once
	if not ok and PassedConfigAt==0 : 
		print('Failed with verify n=1',diff)
		ok, diff = c.verify_configuration(chip_key, n=2 )
	else: 
		#print(ok,' Passed at verify n=1')
		PassedConfigAt=1
	# Try writing twice / reading twice
	if not ok and PassedConfigAt==0 : 
		print('Failed with verify n=2',diff)		
		ok, diff = c.enforce_configuration( chip_key, n=2, n_verify=2 )
	else: 
		print(ok,' Passed at verify n=2')
		PassedConfigAt=2
	if not ok and PassedConfigAt==0 : 
		print('Failed with enforce_configuration n=2,n_verify=2',diff)		
	else: 
		print(ok,' Passed at enforce_configuration n=2,n_verify=2')
		PassedConfigAt=3
	#print('list(c.chips.values()= ',list(c.chips.values()))
	#print('list(c.chips.values())[0]= ',list(c.chips.values())[0])
	#print('list(c.chips.items())[0]= ',list(c.chips.items())[0])
	# Write results of interface config to dated file
	# New dated file paths and names  
	configChipResFileName=DateDirPath+"/chipconfig"+DateDirPath+".csv"
	# If file exists, append with no header
	ChipSN=mychipIDBox[0].get()
	if os.path.exists(configChipResFileName) : 
		configChipResFile=open(configChipResFileName,mode='a')
		outTime=int(time.time())
		configChipResFile.write(str(outTime)+','+str(ChipSN)+','+
								str(io_channel)+','+str(PassedConfigAt)+'\n') 
		configChipResFile.close()
	# else create file with header
	else : 
		configChipResFile=open(configChipResFileName,mode='w')
		configChipResFile.write('TestTime,ChipSN,io_channel,PassedConfigAt\n')
		outTime=int(time.time())
		configChipResFile.write(str(outTime)+','+str(ChipSN)+','+
								str(io_channel)+','+str(PassedConfigAt)+'\n') 
		configChipResFile.close()

	
	if PassedConfigAt==0: # it never passed
		return None
	else:
		chip = list(c.chips.values())[0] # selects 1st chip in chain

	return chip

def init_chips(c):  # only called for v2b or v2a ASICs

	if PacmanVersion == 'RevS1' :
		#c.io.set_reg(0x25014, 0) # enables analog monitor from tile 1 on SMA A
		c.io.set_reg(0x25014, 0x10) # disables analog monitor from all tiles on SMA A
		c.io.set_reg(0x25015, 0x10) # disables SMA B
        	#PACMAN RevS1 powerup settings
		if ASICversion.get() == 'v2c':
			vddd = 29250
			vdda = 43875
		else : # v2a or v2b
			vddd = 43785
			vdda = 43875
		if ASICversion.get() == 'v2b':  # use tile 2 for v2b or v2c for RevS1 pacam
			c.io.set_reg(0x00024132, vdda) # tile 2 VDDA
			c.io.set_reg(0x00024133, vddd) # tile 2 VDDD
			c.io.set_reg(0x00000014, 1) # enable global larpix power
			c.io.set_reg(0x00000010, 0b00000010) # enable tile 2 to be powered
		else: # use tile 1 for v2a for RevS1 pacman 
			c.io.set_reg(0x00024130, vdda) # tile 1 VDDA
			c.io.set_reg(0x00024131, vddd) # tile 1 VDDD
			c.io.set_reg(0x00000014, 1) # enable global larpix power
			c.io.set_reg(0x00000010, 0b00000001) # enable tile 1 to be powered

	else: # older pacman4 version
		#zero supply voltages
		c.io.set_vddd(0) # set vddd 0V
		c.io.set_vdda(0) # set vdda 0V
		
		time.sleep(1)
		#Set correct voltages
		if ASICversion.get() == 'v2c' :
			c.io.set_vddd(vddd_dac=0x8E6C) # set low vddd for v2c(1.2V)
			c.io.set_vdda() # set default vdda (~1.8V)
		else:
			c.io.set_vddd() # set default vddd (~1.8V)
			c.io.set_vdda() # set default vdda (~1.8V)
		# Disable Tile
		c.io.disable_tile()

		# Enable Tile 
		c.io.enable_tile()
		time.sleep(1)

		# measure_currents and voltage
		vddd,iddd = c.io.get_vddd()[1]
		vdda,idda = c.io.get_vdda()[1]
		print('VDDD:',vddd,'mV')
		print('IDDD:',iddd,'mA')
		print('VDDA:',vdda,'mV')
		print('IDDA:',idda,'mA')

	# Is this a v2b setting?  May have to bypass for v2a testing
	_uart_phase = 0
	for ch in range(1,5):
		c.io.set_reg(0x1000*ch + 0x2014, _uart_phase)
		print('set phase:',_uart_phase)


	#reset larpix chips [set sw_rst_cycles to something long, i.e. 256,1024, 
	#set sw_rst_trig to 1, set sw_rst_trig to 0] 
	#(this issues hard reset and syncs the pacman and larpix clocks)
	c.io.reset_larpix(length=10240)
	# resets uart speeds on fpga
	#print('c.network.items()= ',c.network.items())
	for io_group, io_channels in c.network.items():
		for io_channel in io_channels:
			print('set uart speed on group ',io_group,' on channel',io_channel,'...')
			c.io.set_uart_clock_ratio(io_channel, 2, io_group=io_group)

	# First bring up the network using as few packets as possible
	c.io.group_packets_by_io_group = False # this throttles the data rate to avoid FIFO collisions
	c.network.items()

	#if False: 
	for io_group, io_channels in c.network.items():
		#io_channels
		for io_channel in io_channels:
			print("io_group,io_channel:",io_group,",",io_channel)
			c.init_network(io_group, io_channel,differential='True')
			print('Finished init_network')

	if False:  # A test for success of making init_network
		io_group=1
		io_channel=4
		print("io_group,io_channel:",io_group,",",io_channel)
		c.init_network(io_group, io_channel)

	#print(list(c.network[1][4]['miso_ds'].edges()))
	#print(list(c.network[1][4]['miso_us'].edges()))
	#print(list(c.network[1][4]['mosi'].edges()))
	#exit()
	# Brooke Power_up_network.py
	if ASICversion.get() == 'v2b' : 
		#c = larpix.Controller()
		#print('here')
		#c.io = larpix.io.PACMAN_IO(relaxed=True)
		#print('make network')
		#if controller_config is None:
		#	c.add_chip(larpix.Key(1, _default_io_channel, _default_chip_id),version='2b')
		#	c.add_network_node(1, _default_io_channel, c.network_names, 'ext', root=True)
		#	c.add_network_link(1, _default_io_channel, 'miso_us', ('ext',_default_chip_id), 0)
		#	c.add_network_link(1, _default_io_channel, 'miso_ds', (_default_chip_id,'ext'), _default_miso_ds)
		#	c.add_network_link(1, _default_io_channel, 'mosi', ('ext', _default_chip_id), _default_mosi)
		#else:
		#	c.load(controller_config)

		#if reset:
		#	c.io.reset_larpix(length=10240)
			# resets uart speeds on fpga
		#for io_group, io_channels in c.network.items():
		#		for io_channel in io_channels:
		#			c.io.set_uart_clock_ratio(io_channel, clk_ctrl_2_clk_ratio_map[0], io_group=io_group)

		'''  Was forced in Brooke's startup.  No longer needed, as controller.py should do it.
		for chip_key, chip in reversed(c.chips.items()):
			c[chip_key].config.enable_piso_downstream = [0,0,0,1]
			c[chip_key].config.i_tx_diff3=0
			c[chip_key].config.tx_slices3=15
    
			c.write_configuration(chip_key,125)
			c.write_configuration(chip_key,'i_tx_diff3')
			c.write_configuration(chip_key,'tx_slices3')
		'''
               
		#print('Brooke power up complete')
		#print('Writing configuration')
		#while True:
		for chip in c.chips.values():
			if ASICversion.get() == 'v2c' :
				print(c[chip.chip_key].config.enable_piso_downstream) 
				c[chip.chip_key].config.enable_piso_downstream=[1]*4
				print(c[chip.chip_key].config.enable_piso_downstream)
				c.write_configuration(chip.chip_key,'enable_piso_downstream')

		for chip in c.chips.values(): c.write_configuration(chip.chip_key)

		for chip in c.chips.values(): 
			verified,returnregisters=c.verify_configuration(chip.chip_key,n=2)
			print(verified,returnregisters)

		'''  Used during setup, not needed regularly
		while verified == False: 
			chip = list(c.chips.values())[0] # selects 1st chip in chain
			print('Trying again on ',chip)
			print('with config= ',chip.config)
			#c[chip_key].config.enable_posi = [1,1,1,1]
			#c[chip_key].config.test_mode_uart0 = 1
			#c[chip_key].config.test_mode_uart1 = 1
			#c[chip_key].config.test_mode_uart2 = 1
			#c[chip_key].config.test_mode_uart3 = 1
			#c[chip_key].config.v_cm_lvds_tx0 = 0
			#c[chip_key].config.v_cm_lvds_tx1 = 0
			#c[chip_key].config.v_cm_lvds_tx2 = 0
			#c[chip_key].config.v_cm_lvds_tx3 = 0
			c.io.reset_larpix(length=10240)
			c.write_configuration(chip.chip_key)
			verified,returnregisters=c.verify_configuration(chip.chip_key,n=2)
			print(verified,returnregisters)
			print('Tried at ',time.strftime("%H:%M:%S"))
			#time.sleep(20)
			wait_here()
		'''

		#exit()
		#return c


	if ASICversion.get() == 'v2a':
		# Configure the IO for a slower UART and differential signaling
		c.io.double_send_packets = True # double up packets to avoid 512 bug when configuring
		for io_group, io_channels in c.network.items():
			for io_channel in io_channels:
				chip_keys = c.get_network_keys(io_group,io_channel,root_first_traversal=False)
				chip_keys
				for chip_key in chip_keys:
					c[chip_key].config.clk_ctrl = 1
					c[chip_key].config.enable_miso_differential = [1,1,1,1]
					c.write_configuration(chip_key, 'enable_miso_differential')
					c.write_configuration(chip_key, 'clk_ctrl')
		for io_group, io_channels in c.network.items():
			for io_channel in io_channels:
				c.io.set_uart_clock_ratio(io_channel, 4, io_group=io_group)

		c.io.double_send_packets = False
		c.io.group_packets_by_io_group = True

	#for chip in c.chips.values(): print(chip.config)

	# Stolen from Brooke, power_up_network.py
	if False:
		for chip_key, chip in reversed(c.chips.items()):
			c[chip_key].config.enable_piso_downstream = [0,0,0,1]
			c[chip_key].config.i_tx_diff3=0
			c[chip_key].config.tx_slices3=15
			c.write_configuration(chip_key,125)
			c.write_configuration(chip_key,'i_tx_diff3')
			c.write_configuration(chip_key,'tx_slices3')


	print('Writing configuration')
	#while True:
	print(c[chip.chip_key].config.enable_piso_downstream) 
	if ASICversion.get() == 'v2c' :
		print(c[chip.chip_key].config.enable_piso_downstream) 
		c[chip.chip_key].config.enable_piso_downstream=[1]*4
		print(c[chip.chip_key].config.enable_piso_downstream)

	for chip in c.chips.values(): c.write_configuration(chip.chip_key)

	for chip in c.chips.values(): c.verify_configuration(chip.chip_key,n=2)

	chip = list(c.chips.values())[0] # selects 1st chip in chain
	#chip = list(c.chips.values())[1] # selects 2nd chip in chain
	#chip = list(c.chips.values())[2] # selects 3rd chip in chain
	#chip = list(c.chips.values())[3] # selects 3rd chip in chain
	print(chip)
	print(chip.chip_key)
	#print(chip.config)
	c.write_configuration(chip.chip_key)
	verified,returnregisters=c.verify_configuration(chip.chip_key,n=2)
	if verified == False : # try again
		print(verified,returnregisters)
		verified,returnregisters=c.verify_configuration(chip.chip_key,n=2)

	if verified == False : # exit
		print(verified,returnregisters)
		#Disable chip power and interface at end
		print('Configuration failed, exiting')
		#powerdown(c)
		return

	print('Finished configuring chip ',chip)
	return chip

def enable_channel(chan):
	# Configure one channel to be on.
	chip.config.channel_mask = [1] * NumASICchannels  # Turn off all channels
	chip.config.channel_mask[chan]=0  # turn ON this channel
	c.write_configuration(chip.chip_key)
	c.verify_configuration(chip.chip_key,n=2)

# Set global threshold
def setGlobalThresh(c,chip,Thresh=50):
	#print(chip.chip_key)	
	#print(id(chip.config))
	chip.config.threshold_global=Thresh
	c.write_configuration(chip.chip_key)
	#c.verify_configuration(chip.chip_key,n=2)

# Turn on a series of channels (a list would be better) on analog
# monitor and loop to the next one every 5 seconds.
def AnalogDisplayLoop(c,chip,firstChan=0,lastChan=NumASICchannels-1):
	for chan in range(firstChan,lastChan+1):
		AnalogDisplay(c,chip,chan)
		time.sleep(10)
		wait_here()

# set a really long periodic reset (std=4096, this is 1M)
#chip.config.reset_cycles=1000000

# Turn on and display one channel on analog monitor
def AnalogDisplay(c,chip,chan):
	# Configure one channel to be on.
	chip.config.channel_mask = [1] * NumASICchannels  # Turn off all channels
	chip.config.channel_mask[chan]=0  # turn ON this channel
	# Enable analog monitor on one channel at a time
	c.enable_analog_monitor(chip.chip_key,chan)
	print("Running Analog mon on channel ",chan)
	c.write_configuration(chip.chip_key)
	c.verify_configuration(chip.chip_key,n=2)
	#time.sleep(5) # move to the loop
	#c.disable_analog_monitor(chip.chip_key)

# Loop over approximately all channels and output analog mon for 5 seconds.
#AnalogDisplayLoop(0,NumASICchannels-1)

# Capture Data for channels in sequence

def ReadChannelLoop(c,chip,firstChan=0,lastChan=NumASICchannels-1,monitor=0):
	#sleeptime=0.1
	#c.start_listening()
	#for chan in reversed(range(firstChan,lastChan+1)): # used for a test
	for chan in range(firstChan,lastChan+1):
		#print("Running chip ",chip," chan ",chan)
		if TileChannelMask[chan]!=0: 
			ReadChannel(c,chip,chan,monitor)
		#time.sleep(sleeptime)
	#c.stop_listening()
	chip.config.channel_mask = [1] * NumASICchannels  # Turn off all channels
	chip.config.periodic_trigger_mask = [1] * NumASICchannels  # Turn off all channels
	c.write_configuration(chip.chip_key)


def ReadChannel(c,chip,chan,monitor=0):
	# Configure one channel to be on.
	print("Running chip ",chip," chan ",chan)
	chip.config.channel_mask = [1] * NumASICchannels  # Turn off all channels
	chip.config.channel_mask[chan]=0  # turn ON this channel
	chip.config.periodic_trigger_mask = [1] * NumASICchannels  
	chip.config.periodic_trigger_mask[chan]=0  # turn ON this channel
	#if chan < NumASICchannels-1 : 
	#	chip.config.channel_mask[chan+1]= not TileChannelMask[chan+1]
	#if chan < NumASICchannels-2 : 
	#	chip.config.channel_mask[chan+2]= not TileChannelMask[chan+2]
	#if chan < NumASICchannels-3 : 
	#	chip.config.channel_mask[chan+3]= not TileChannelMask[chan+3]
	#for thischan in range(0,NumASICchannels):   # turn ON ALL channels (test 20210331)
	#	chip.config.channel_mask[thischan] = not TileChannelMask[thischan]
	if monitor==1:
		# Enable analog monitor on channel
		c.enable_analog_monitor(chip.chip_key,chan)
		print("Running Analog mon for Pulser on channel ",chan)
	c.write_configuration(chip.chip_key)
	print('***************************************')
	print('****      READ CHANNEL             ****')
	print('***************************************')
	#print(chip.config)
	#c.verify_configuration(chip.chip_key,n=2)
	loop=0
	looplimit=1
	while loop<looplimit :
		# Read some Data (this also delays a bit)
		c.run(0.1,'test')
		#print(c.reads[-1])
		print("read ",len(c.reads[-1])," packets")
		#wait_here()
		loop=loop+1


def get_baseline_selftrigger(c,chip):
	# Capture Baseline for all channels one by one

	# Turn on periodic_reset
	chip.config.enable_periodic_reset = 1 
	# Reduce global threshold to get baseline data
	chip.config.threshold_global=5 
	# Extend the time for conversion as long as possible
	#chip.config.sample_cycles=150
	#chip.config.sample_cycles=1 #(set to default starting 2/21/2020)
	c.write_configuration(chip.chip_key)
	c.verify_configuration(chip.chip_key,n=2)

	subprocess.run(["rm","testing.h5"])

	#logger declared and switched enabledc.
	c.logger = HDF5Logger("testing.h5", buffer_length=1000000)
	#c.logger = HDF5Logger("testing.h5", buffer_length=10000)
	c.logger.enable()
	c.logger.is_enabled()

	c.verify_configuration(chip.chip_key,n=2)
	print(chip.config)

	ReadChannelLoop(c,chip,0,NumASICchannels-1,0)

	print("the end")

	c.logger.disable()
	#c.logger.flush()
	#c.logger.close()

	import socket_baselines

def get_baseline_periodicselftrigger(c,chip):
	# Capture Baseline for all channels one by one

	# Turn on periodic_reset
	chip.config.enable_periodic_reset = 1 
	#chip.config.periodic_reset_cycles = 1000000 
	# Reduce global threshold to get baseline data
	chip.config.threshold_global=255 
	# Extend the time for conversion as long as possible
	#chip.config.sample_cycles=150
	#chip.config.sample_cycles=1 #(set to default starting 2/21/2020)
	# for v2 sample_cycles -> adc_hold_delay
	#chip.config.adc_hold_delay=150
	#chip.config.adc_hold_delay=1 #(set to default starting 2/21/2020)
	# enable periodic trigger
	chip.config.enable_periodic_trigger=1
	chip.config.periodic_trigger_mask= [1] * NumASICchannels  # Turn off all channels
	# swapped line above 0 (on) to 1 (off) on 17-NOV-2021 LMM
	# I suspect this was causing the leakage.  Different behavior v2 and v2b with masking.
	chip.config.enable_hit_veto = 0
	# set trigger period (100ns*period_trigger_cycles)
	chip.config.periodic_trigger_cycles=1000 # 1k = 0.1ms
	#chip.config.periodic_trigger_cycles=10000 # 10k = 1ms
	#chip.config.periodic_trigger_cycles=20000 # 20k = 2ms
	#chip.config.periodic_trigger_cycles=100000 # 100k = 10ms
	#chip.config.periodic_trigger_cycles=7500000 # 750k = 75ms
	#chip.config.periodic_trigger_cycles=1000000 # 1000k = 100ms
	c.write_configuration(chip.chip_key)
	c.verify_configuration(chip.chip_key,n=2)

	subprocess.run(["rm","testing.h5"])

	#logger declared and switched enabled.
	c.logger = HDF5Logger("testing.h5", buffer_length=1000000)
	#c.logger = HDF5Logger("testing.h5", buffer_length=10000)
	c.logger.enable()
	c.logger.is_enabled()

	#c.verify_configuration(chip.chip_key,n=2)
	#print(chip.config)
	print("Starting ReadChannelLoop...")

	Monitor = 0 # display analog mon (1) or not (0) 
	ReadChannelLoop(c,chip,0,NumASICchannels-1,Monitor)

	print("the end")
	textBox.config(bg="yellow")
	doneSong.play()
	window.update()	

	c.logger.disable()
	#c.logger.flush()
	#c.logger.close()

	# turn off periodic trigger channels
	chip.config.periodic_trigger_mask= [1] * NumASICchannels
	chip.config.enable_periodic_trigger=0
	c.write_configuration(chip.chip_key)

	#import socket_baselines

	run_Popen=True
	if run_Popen :
		# Run socket_baselines in subprocess to allow killing
		#cmd=['python socket_baselines.py']
		if ASICversion.get() == 'v2a':
			cmd=['python socket_baselines_v2astd.py']
		elif ASICversion.get() == 'v2b':
			cmd=['python socket_baselines_v2bstd.py',DateDirPath]
		else:
			print('*** Running v2b specific baselines, but ASIC !=v2b No idea quality of results ***')
			cmd=['python socket_baselines_v2bstd.py',DateDirPath]
		start_time=time.time()
		with Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
			FirstLine=True
			print('hopefully running socket_baselines.py')
			for line in p.stdout:
				if FirstLine :
					mypid=line # first line should just be the PID from the subprocess
					FirstLine=False
				print(line, end='') # process line here
				dt=time.time()-start_time
				#print('dt=',dt)
				if dt > 30 : 
					# PID of process sent as first output (set in socket_baselines.py)
					print('mypid socket_baselines is ',mypid)
					os.kill(int(mypid),signal.SIGKILL)

		nBadBaselineChannels=p.returncode
		#if p.returncode != 0:
			#nBadBaselineChannels=p.returncode
			#raise CalledProcessError(p.returncode, p.args)
	else : 
		os.environ['socket_PlotBaselineChannels']=LoadHTMLplotsState.get()
		runpy.run_module(mod_name='socket_baselines')
		nBadBaselineChannels=os.getenv('socket_BadBaselineChannels')
		print(nBadBaselineChannels)

	if int(nBadBaselineChannels) == 0 :
		textBox.config(bg="green")
		successSong.play()
		window.update()	
	else : 
		textBox.config(bg="red") # flashing? 
		sadSong.play()
		window.update()	

	return nBadBaselineChannels

def get_baseline_periodicexttrigger(c,chip):
	# Capture Baseline for all channels

	# Turn on periodic_reset
	chip.config.enable_periodic_reset = 1 
	# Reduce global threshold to get baseline data
	chip.config.threshold_global=255 
	# Extend the time for conversion as long as possible
	#chip.config.sample_cycles=255
	# No more sample_cycles in v2?
	#chip.config.sample_cycles=1 #(set to default starting 2/21/2020)
	c.write_configuration(chip.chip_key)
	c.verify_configuration(chip.chip_key,n=2)

	subprocess.run(["rm","testing2.h5"])

	chip.config.channel_mask = [0] * NumASICchannels  # Turn ON all channels
	chip.config.external_trigger_mask = [0] * NumASICchannels  # Turn ON all channels
	c.write_configuration(chip.chip_key)
	c.verify_configuration(chip.chip_key,n=2)
	print(chip.config)

	#logger declared and switched enabledc.
	c.logger = HDF5Logger("testing2.h5", buffer_length=1000000)
	#c.logger = HDF5Logger("testing.h5", buffer_length=10000)
	c.logger.enable()
	c.logger.is_enabled()

	c.run(10,'test')
	print("read ",len(c.reads[-1]))
	print("the end")

	c.logger.disable()
	#c.logger.flush()
	#c.logger.close()

	import socket_baselines2


def PulseChannelLoop(firstChan=0,lastChan=NumASICchannels-1,amp=0,monitor=0):
	for chan in range(firstChan,lastChan+1):
		PulseChannel(chan,amp,monitor)

def PulseChannel(chan,amp=0,monitor=0):
        # Configure one channel to be on.
        chip.config.channel_mask = [1] * NumASICchannels  # Turn off all channels
        chip.config.channel_mask[chan]=0  # turn ON this channel
        if (monitor==1):
                # Enable analog monitor on channel
                c.enable_analog_monitor(chip.chip_key,chan)
                print("Running Analog mon for Pulser on channel ",chan)
        c.write_configuration(chip.chip_key)
        #c.verify_configuration(chip.chip_key,n=2)
        loop=0
        looplimit=5
        while loop<looplimit :
                c.enable_testpulse(chip.chip_key, [chan], start_dac=200)
                c.issue_testpulse(chip.chip_key, amp, min_dac=100)
                # Read some Data (this also delays a bit)
                #c.run(1,'test')
                print(c.reads[-1])
                loop=loop+1

def get_charge_injection():
	# Run some pulser 

	# Turn on periodic_reset
	chip.config.enable_periodic_reset = 1 
	# Reduce global threshold to get some data
	chip.config.global_threshold=50 
	# Extend the time for conversion as long as possible
	chip.config.sample_cycles=255
	chip.config.channel_mask = [1] * NumASICchannels  # Turn off all channels
	chip.config.external_trigger_mask = [1] * NumASICchannels  # Turn OFF ext trig all channels
	c.write_configuration(chip.chip_key)
	c.verify_configuration(chip.chip_key,n=2)
	PulseChannelLoop(0,NumASICchannels-1,10,0)


def get_leakage_data():
	# This part is not quite ready yet.
	# Still not ready 20200212 - required thresh values depend on channel 
	# and you only want ot do it on channels that are good so far.

	# Turn off periodic_reset
	chip.config.enable_periodic_reset = 0 # turn off periodic reset
	chip.config.channel_mask = [1] * NumASICchannels  # Turn off all channels
	c.write_configuration(chip.chip_key)
	c.verify_configuration(chip.chip_key,n=2)

	for thresh in [25,27,30,35]:
		setGlobalThresh(thresh)
		outfile = "testing" + str(thresh) + ".h5"
		print("Writing ",outfile)
		#logger declared and switched enabledc.
		c.logger = HDF5Logger(outfile, buffer_length=1000000)
		#c.logger = HDF5Logger("testing.h5", buffer_length=10000)
		c.logger.enable()
		c.logger.is_enabled()
		# Configure one channel to be on.
		for chan in range(NumASICchannels):	
			print("running channel ",chan)
			if socket_baselines.mean[chan] > 240 or socket_baselines.sdev[chan] < 2 : continue
			chip.config.channel_mask = [1] * NumASICchannels  # Turn off all channels
			chip.config.channel_mask[chan]=0  # turn ON this channel
			c.write_configuration(chip.chip_key)
			c.verify_configuration(chip.chip_key,n=2)
			# Read some Data (this also delays a bit)
			c.run(1,'test')
			print(c.reads[-1])
			print("the end")
		c.logger.disable()
		#c.logger.flush()
		c.logger.close()

def get_ThreshLevels(c,chip):


	#ChipSN = mychipIDBox[0].get()
	tempstatus = h5py.File("CurrentRun.tmp",mode='r')
	dset = tempstatus['CurrentRun']
	ChipSN = dset.attrs['ChipSN']
	tempstatus.close()

	#open hdf5 output file
	#ThreshDataFile = h5py("RateVsThreshData.h5",mode='a')
	RateThreshFrame = pd.DataFrame(columns = ['runtime','thresh','numsamples','dt','ChanName','Chan','ChipSN'])
	runtime=time.time()

	for chan in range(NumASICchannels):	
		if TileChannelMask[chan]==1: 
			print("running channel ",chan)
			chip.config.channel_mask = [1] * NumASICchannels  # Turn off all channels
			chip.config.channel_mask[chan]=0  # turn ON this channel
			c.write_configuration(chip.chip_key)
			c.verify_configuration(chip.chip_key,n=2)
			thresh=128
			step = 16
			rate = 0
			sampleTime = 0.30  # if you use smaller, need to use packet times for better precision
			stepthresh = 10
			while rate < 300 and ( thresh >= 1 and step >= 2 ) :
				setGlobalThresh(c,chip,thresh)
				# Read some Data (this also delays a bit)
				c.run(sampleTime,'test')
				#numsamples=len(c.reads[-1]['packet_type'==0])
				numsamples=len(c.reads[-1])
				print("Read ",numsamples," samples")
				# find duration of samples (first/last)
				sampleIter=0
				firstTime=0
				lastTime=0
				while sampleIter<numsamples :
					#if c.reads[-1].packets[sampleIter].chip_key != None :
					if c.reads[-1].packets[sampleIter].packet_type == 0 :
						#print(c.reads[-1].packets[sampleIter].packet_type)
						if c.reads[-1].packets[sampleIter].channel_id == chan :
							firstTime = c.reads[-1].packets[sampleIter].timestamp
							sampleIter=numsamples # To end the loop 
							#print("End time at ",numsamples-sampleIter-1)
					sampleIter=sampleIter+1
				sampleIter=0
				while sampleIter<numsamples :
					#if c.reads[-1].packets[sampleIter].packet_type == Packet_v2.DATA_PACKET :	
					#if c.reads[-1].packets[numsamples-sampleIter-1].chip_key != None :
					if c.reads[-1].packets[numsamples-sampleIter-1].packet_type == 0 :
						#print(c.reads[-1].packets[numsamples-sampleIter-1].packet_type)
						if c.reads[-1].packets[numsamples-sampleIter-1].channel_id == chan :
							lastTime = c.reads[-1].packets[numsamples-sampleIter-1].timestamp
							sampleIter=numsamples # to end the loop
							#print("End time at ",numsamples-sampleIter-1)
					sampleIter=sampleIter+1
				dt = lastTime-firstTime 
				if dt < 0 : dt =dt+2**24
				if dt == 0 : dt = dt+sampleTime*5E6
				dt = dt / 5E6
				#print(dt,"<- delta and first time: ",firstTime,"Last time: ",lastTime)
				#rate = numsamples/sampleTime			
				rate = numsamples/dt
				print("Channel ",chan," Thresh ",thresh," Rate ",rate)
				textchan = 'ch{:02d}'.format(chan)
				RateThreshFrame=RateThreshFrame.append({'runtime':runtime,'thresh':thresh,'numsamples':numsamples,
				'dt':dt,'ChanName':textchan,'Chan':chan,'ChipSN':ChipSN},ignore_index=True)
				print('len(RateThreshFrame.index)=',len(RateThreshFrame.index))
				thresh = thresh - step 
				if rate > stepthresh and step > 2 :
					thresh = thresh + step +step
					step = int(step/2)
					if step < 4 : sampleTime=1.0
					if rate < 100 :	stepthresh = stepthresh + stepthresh
			setGlobalThresh(c,chip,255)
			#print("c.reads is ",len(c.reads)," long")
			#print("c.reads is ",sys.getsizeof(c.reads)," long")
			c.reads.clear()
			#print("c.reads is ",len(c.reads)," long")
			#print("c.reads is ",sys.getsizeof(c.reads)," long")
			print("the end") # of chan loop


	#summaryFrame.to_csv("t.csv",mode='a',header=True)
	#RateThreshFrame.to_csv("RateThresh.csv",mode='a',header=False)
	RateThreshFrame.to_hdf("RateThresh.h5",mode='a',key='RateVsThreshV1')

def RunControl():
	HOST = '192.168.12.139'  # apdlab pc interface address 
	PORT = 38630        # Port to listen on (non-privileged ports are > 1023)

	Hello='H\r'
	Start='S\r'
	Ready='R\r'
	EOL='EOL\r'
	Result0='0\r'
	Result1='1\r'
	Result2='2\r'
	Result3='3\r'
	Result4='4\r'
	Result5='5\r'
	Result6='6\r'
	Result7='7\r'
	Result8='8\r'
	Result9='9\r'

	if UseTCPIPControlState.get() == '0' :  # if TCPIPControl is not checked, just RunTests()
		totalBadChannels = RunTests()  # Single chip test mode
		# Increment SN if check box enabled
		if SNAutoIncrement.get() == '1' :
			SNUp()

	else :
		window.children['!frame'].children['!button'].configure(text='Running TCPIPcontrol...')
		#tsp.DumbFunc('in RunControl')
		# Start the server
		print('Starting TCPIP server connection')
		conn, addr = tsp.OpenSocketConn(HOST,PORT)
		while conn : # was while True : If TCP no longer works, change it back 20211214 LMM
			message = tsp.CheckSocketForData(conn)
			if message == bytes(Hello,"utf-8") :
				print('Received Hello from Chip Handler')
				#Send Ready (or EOL) back
				print('Sending Ready to Chip Handler')
				conn.sendall(bytes(Ready,"utf-8"))
			# Load a chip
			FirstTry = True
			# Wait for Start
			message = tsp.CheckSocketForData(conn)
			if message == bytes(Start,"utf-8") :
				print('Received Start from Chip Handler')
				#Send Ready (or EOL) back
				print('Starting tests')
				# Run Tests
				ResultNum=RunTests()
				# Does this section need a full Hello/Ready? probably
				if FirstTry and not ResultNum==0 : 
					#send 8 to retry socket insertion and rerun tests
					# requires double plunge enable for this result in chip handler
					print('Result was ',ResultNum,' sending ',Result8,' to retry')
					conn.sendall(bytes(Result8,"utf-8"))
					FirstTry = False
					message = tsp.CheckSocketForData(conn)
					if message == bytes(Start,"utf-8") :
						print('Received Start from Chip Handler')
						#Send Ready (or EOL) back
						print('Starting tests')
						# Run Tests
						ResultNum=RunTests()
				#time.sleep(5)
				#ResultNum=0 # Fake result for testing
				# Send results to Chip Handler
				if ResultNum == 0 : 
					print('Result was ',ResultNum,' sending ',Result1)
					conn.sendall(bytes(Result1,"utf-8"))
				elif ResultNum < 0 : 
					print('Result was ',ResultNum,' sending ',Result3)
					conn.sendall(bytes(Result3,"utf-8"))
				else: 
					print('Result was ',ResultNum,' sending ',Result2)
					conn.sendall(bytes(Result2,"utf-8"))
			# Get another chip (what happens after 180 tests?)
			# Increment SN if check box enabled
			if SNAutoIncrement.get() == '1' :
				SNUp()
		# Close the server
		return

#def RunTests(c,chip):
def RunTests():

	#Change run button to running
	window.children['!frame'].children['!button'].configure(text='Running...')
	#make text box red
	textBox.config(bg="red")
	# grey out selection boxes
	for myiter in testCheckframe.children:
		# print('disabling ', myiter)
		testCheckframe.children[myiter].state(['disabled'])
		window.update()


	if ASICversion.get() == 'v2a': setv2channelmask()
	print("Running tests for Chip SN: ",mychipIDBox[0].get())
	ChipSN=mychipIDBox[0].get()

	testID=0
	currentTests=[]
	for test in buttonVars:
		currentTests.append(buttonVars[testID].get())
		testID=testID+1

	tempstatus = h5py.File("CurrentRun.tmp",mode='w')
	dset = tempstatus.create_dataset("CurrentRun",dtype='i')
	dset.attrs['ChipSN']=ChipSN
	dset.attrs['currentTest']=currentTests
	dset.attrs['UseTCPIPControl']=UseTCPIPControlState.get()
	dset.attrs['LoadHTMLplot']=LoadHTMLplotsState.get()
	#dset.attrs['v2bASIC']=v2bState.get()
	#dset.attrs['v2cASIC']=v2cState.get()
	dset.attrs['SNAutoUp']=SNAutoIncrement.get()
	dset.attrs['ASICversion']=ASICversion.get()
	# Don't save or restore SNfromFile, since input file needs selection each time
	tempstatus.close()

	#INIT BOARD/CHIP and test all 4 comm links
	init_chip_results=0
	for io_channel in [4,3,2,1]: 
		if io_channel != 4 : c.io.cleanup() # stop zmq io threads needed if you make a new controller
		c=init_controller() # create a new clean controller instance
		chip = 0
		if ASICversion.get() == 'v2a' or ASICversion.get() == 'v2b' : # run working intialization of v2b and v2a chips
			#init_board(c) # defaults to channel 1
			#init_board(c,io_channel)
			init_board_base(c,io_channel)
			chip=init_chips(c)	 
		elif ASICversion.get() == 'v2c' or ASICversion.get() == 'v2d' : # run v2c specific chip initialization. (should work for v2b also, and v2d)
			chip = init_chips_v2c(c,io_channel) # does work of init_board_base and init_chips
		else: 
			print('can not get ASICversion.get(), found ',ASICversion.get())
		print(chip)
		#print('c.chips after init board/chip')
		#print(c.chips)
		#print(chip.config)
		#exit() 
		if chip == None : 
			print('Failed in init_chips for io_channel ',io_channel)
			init_chip_results=init_chip_results+pow(2,(io_channel-1))

	# Write results of interface config to dated file
	global DateDirPath
	DateDirPath = time.strftime("%y%m%d")
	BatchNum=0
	BatchPath=DateDirPath+"-"+str(BatchNum)
	while os.path.exists(BatchPath) : # Batch exists
		BatchNum = BatchNum+1 # increment until it doesn't
		BatchPath=DateDirPath+"-"+str(BatchNum)
	DateDirPath=BatchPath # Use the BatchPath for the directory and filenames
	if not os.path.exists(DateDirPath) : os.mkdir(DateDirPath)
    # New dated file paths and names  
	configResFileName=DateDirPath+"/netconfig"+DateDirPath+".csv"
	# If file exists, append with no header
	if os.path.exists(configResFileName) : 
		configResFile=open(configResFileName,mode='a')
		outTime=int(time.time())
		configResFile.write(str(outTime)+','+str(ChipSN)+','+str(init_chip_results)+'\n') 
		configResFile.close()
	# else create file with header
	else : 
		configResFile=open(configResFileName,mode='w')
		configResFile.write('TestTime,ChipSN,init_chip_results\n')
		outTime=int(time.time())
		configResFile.write(str(outTime)+','+str(ChipSN)+','+str(init_chip_results)+'\n') 
		configResFile.close()
	# No point doing further tests if chip config failed
	if init_chip_results !=0 :
		powerdown(c)
		return -init_chip_results 

	#c=init_controller()
	#init_board(c,4)
	#chip=init_chips(c)	 
	#print(chip)

	#test flipping bits in config register and see that they configure
	if ASICversion.get() == 'v2d':
		register_results=0
		print('##############################################################')
		print('##############################################################')
		print('###     SKIPPING FLIP BIT CHECK for V2D                    ###')
		print('##############################################################')
		print('##############################################################')
	else:
		register_results = test_config_registers(c,chip)	
		if register_results != 0 : 
			print('test_config_registers returned ',register_results)
			if register_results == 1 :
				print('Failed with bit flipping in register')
			if register_results == 2 :
				print('Failed with config in test_config_registers')
	#print(c.network)	
	#for io_group, io_channels in c.network.items():
	#	for io_channel in io_channels:
	#		print('reset uart speed on channel',io_channel,'...')
	#		c.io.set_uart_clock_ratio(io_channel, 2, io_group=io_group)
	#c.reset_network(1,4)
	#c.io.cleanup() # stop zmq io threads needed if you make a new controller
	#c=init_controller()
	#init_board(c,3)
	#chip=init_chips(c)	 
	#print(chip)	
	#print('##############################################################')
	#print('##############################################################')
	#print('###     SKIPPING CHANNEL 2 since PISO1 is broken on board  ###')
	#print('##############################################################')
	#print('##############################################################')
	#c.io.cleanup() # stop zmq io threads needed if you make a new controller
	#c=init_controller()
	#init_board(c,2)
	#chip=init_chips(c)	 
	#print(chip)	

	#c.io.cleanup() # stop zmq io threads needed if you make a new controller
	#c=init_controller()
	#init_board(c,1)
	#chip=init_chips(c)	 
	#print(chip)	

	# No point doing further tests if register writing failed
	if register_results != 0 :
		powerdown(c)
		return -100*register_results 

	# Set global threshold
	setGlobalThresh(c,chip,255)

	# Enable analog monitor on one channel
	c.enable_analog_monitor(chip.chip_key,28)
	c.write_configuration(chip.chip_key)
	c.verify_configuration(chip.chip_key,n=2)

	# Turn on periodic_reset
	#chip.config.enable_periodic_reset = 1 # turn on periodic reset
	#c.write_configuration(chip.chip_key)
	#c.verify_configuration(chip.chip_key,n=2)

	# Turn off periodic_reset
	chip.config.enable_periodic_reset = 0 # turn off periodic reset
	# Turn on periodic_reset
	chip.config.enable_periodic_reset = 1 # turn on periodic reset

	# set a really long periodic reset (std=4096)
	#chip.config.periodic_reset_cycles=4096 # 819us
	#chip.config.periodic_reset_cycles=5096 # 1019us
	chip.config.periodic_reset_cycles=100000 # 20ms
	#chip.config.periodic_reset_cycles=1000000 # 200ms
	#chip.config.periodic_reset_cycles=10000000 # 2s

	if ASICversion.get() == 'v2b':
		#v2b defaults for socket tester
		#set ref vcm  (77 def = 0.54V)
		chip.config.vcm_dac=45
		#set ref vref  ( 219 def = 1.54V)
		chip.config.vref_dac=187
	elif ASICversion.get() == 'v2c':
		#v2c defaults for socket tester
		#set ref vcm  (77 def = 0.54V)
		chip.config.vcm_dac=50
		#set ref vref  ( 219 def = 1.54V)
		chip.config.vref_dac=192
	elif ASICversion.get() == 'v2d':
		#v2c defaults for socket tester
		#set ref vcm  (77 def = 0.54V)
		chip.config.vcm_dac=45
		#set ref vref  ( 219 def = 1.54V)
		chip.config.vref_dac=187
	elif ASICversion.get() == 'v2a':
		# setting for v2a 
		# 77 too high, all are at 0, 50 sent some down to zero, 
		# try 40 still a few close to 0, try 35, that looks comfortable
		#set ref vcm  (77 def = 0.54V)
		chip.config.vcm_dac=35
		#set ref vref  ( 219 def = 1.54V)
		chip.config.vref_dac=177
		#set ref current.  (11 for RT, 16 for cryo)
		#chip.config.ref_current_trim=16
		#set ibias_csa  (8 for default, range [0-15])
		#chip.config.ibias_csa=12
	else:
		print('*** Not running v2a or v2b specific vcm and vref, using defaults ***')

	chip.config.pixel_trim_dac = [31] * NumASICchannels

	c.write_configuration(chip.chip_key)
	c.verify_configuration(chip.chip_key,n=2)

	# Disable analog monitor (any channel)
	c.disable_analog_monitor(chip.chip_key)
	c.write_configuration(chip.chip_key)
	c.verify_configuration(chip.chip_key,n=2)

	#print(chip.config)
        
	# END INIT BOARD/CHIP

	# Update progress boxes along the way
	#time.sleep(10)
	#find checkboxes that are enabled and run test
	testID=0
	totalBadChannels=0
	for test in testList:
		#testFunctions.append(testFunctionNames[testID])
		#print(test)
		print(buttonVars[testID].get()," = ",testList[testID])
		if buttonVars[testID].get()=='0': 
			print("Skipping ",testList[testID])
		else :
			print("Running ",testList[testID])
			func = globals()[testFunctionNames[testID]](c,chip)
			print("Returned ",func," bad channels")
			totalBadChannels=totalBadChannels+int(func)
		#	text=test,variable=buttonVars[testID],command=printStatus))
		testID=testID+1

	#run test
	#textBox.config(bg="green")	
	#report done

	#Disable chip power and interface at end
	# Disable Tile
	c.io.disable_tile()
	#zero supply voltages
	c.io.set_vddd(0) # set vddd 0V
	c.io.set_vdda(0) # set vdda 0V

	# Reenable boxes
	#testCheckframe.state(['!disabled'])
	for myiter in testCheckframe.children:
		# print('disabling ', myiter)
		testCheckframe.children[myiter].state(['!disabled'])
		window.update()

	window.children['!frame'].children['!button'].configure(text='Run Test')
	return totalBadChannels

def SNDown(): #reduce SN last digits of SN by one
	if SNfromFile.get() == '0':
		ChipSN = mychipIDBox[0].get()
		NumSN = int(ChipSN[2:])
		#print(ChipSN,NumSN)
		NumSN = NumSN -1
		ChipSN = ChipSN[:2]+format(NumSN,"05d")
		mychipIDBox[0].delete(0,'end')
		mychipIDBox[0].insert(0,ChipSN)
	else:
		global SNList
		ChipSN = mychipIDBox[0].get()
		#print(SNList)
		SNIndex=SNList.index([ChipSN])
		#print(ChipSN,SNIndex)
		if SNIndex==0: print("Already at start of list")
		else: SNIndex = SNIndex-1
		ChipSN=SNList[SNIndex][0]
		mychipIDBox[0].delete(0,'end')
		mychipIDBox[0].insert(0,ChipSN)

def SNUp(): # increase last digits of SN by one
	if SNfromFile.get() == '0':
		ChipSN = mychipIDBox[0].get()
		NumSN = int(ChipSN[2:])
		#print(ChipSN,NumSN)
		NumSN = NumSN +1
		ChipSN = ChipSN[:2]+format(NumSN,"05d")
		mychipIDBox[0].delete(0,'end')
		mychipIDBox[0].insert(0,ChipSN)
	else:
		global SNList
		ChipSN = mychipIDBox[0].get()
		#print(SNList)
		SNIndex=SNList.index([ChipSN])
		#print(ChipSN,SNIndex)
		if SNIndex==len(SNList)-1: print("Already at end of list")
		else: SNIndex = SNIndex+1
		ChipSN=SNList[SNIndex][0]
		mychipIDBox[0].delete(0,'end')
		mychipIDBox[0].insert(0,ChipSN)

def SNAutoUp(): # Set Button to increase last digits of SN by one at end of test
	# Toggle 
	#print("SNAutoIncrement=",SNAutoIncrement.get())
	return

def selectFile(defaultFile):
	filetypes = (('csv files','*.csv'),('text files','*.txt'),('All files','*.*'))
	filename = fd.askopenfilename(
		title='Serial Number file name',
		initialdir='.',
		initialfile=defaultFile,
		filetypes=filetypes)
	return filename

def UseSNFile(): # Use SN file list for serial numbers
	# Toggle 
	#print("SNAutoIncrement=",SNAutoIncrement.get())
	# Read in a list of Serial Numbers (SNList)
	if SNfromFile.get() == '1':
		SNAutoIncrement.set('1')
		global SNList
		SNcsvFile = selectFile('SNList.csv') 
		#with open('SNList.csv',newline='') as snfile:
		with open(SNcsvFile,newline='') as snfile:
			reader = csv.reader(snfile)
			SNList = list(reader)
		#print(SNList.index(['2B13303']))
		SNarray=np.array(SNList)
		UniqueSN=np.unique(SNarray)
		if len(SNList) == len(UniqueSN):
			print('read ',len(SNList),' serial numbers from ',SNList[0][0],' to ',SNList[-1][0])
		else:
			print('Not all SN are unique, check SNFile')
		# Set the SN text to the "first" entry
		mychipIDBox[0].delete(0,'end')
		mychipIDBox[0].insert(0,SNList[0][0])
		# Adapt SNUp and SNDown to iterate through SNList
	return

def UseTCPIPControl(): # Set Button to increase last digits of SN by one at end of test
	# Toggle 
	#print("UseTCPIPControl=",UseTCPIPControlState.get())
	return

def NewASICVersion(event):  # ASIC selection changed
	#print('New ASIC version=',ASICversion.get())
	return
		  
def trygui():
	#window = tk.Tk()
	#global runPeriodicBaseline
	#global runBaseline
	mainframe = ttk.Frame(window, padding="5") # padding at edge of window
	mainframe.grid(column=0, row=0, sticky=("N, W, E, S"))
	#window.columnconfigure(0, weight=1,uniform='a')
	#window.rowconfigure(0, weight=1,uniform='a')
	window.title("ASIC Testing Controller")
	window.geometry('+100+50')

	mylabel = ttk.Label(mainframe, text="ASIC testing")
	mylabel.grid(column=0,row=0)


	mybutton= ttk.Button(mainframe,text="Run Tests",command= lambda:RunControl())
	mybutton.grid(column=0,row=1)

	global mychipIDBox
	mychipIDBox = []
	def deploySN():
		#print('numChipVar = ',numChipVar)
		if int(numChipVar.get()) > len(mychipIDBox):
			for ChipNum in range(len(mychipIDBox)+1,int(numChipVar.get())+1):
				#print(ChipNum)
				mychipIDBox.append(ttk.Entry(SNframe,width=8))
				mychipIDBox[ChipNum-1].grid(column=4,
					row=ChipNum,sticky='E',padx=10) 
		if int(numChipVar.get()) < len(mychipIDBox):
			for ChipNum in range(len(mychipIDBox),int(numChipVar.get()),-1):
				#print(ChipNum)
				mychipIDBox[ChipNum-1].state(['disabled'])
		for ChipNum in range(1,int(numChipVar.get())+1):
			mychipIDBox[ChipNum-1].state(['!disabled'])

	global testList,testFunctionNames
	testList = ["Baseline Periodic SelfTrig",
			"Baseline Ext Trig",
			"Thresh Levels",
			"Leakage Data",
			"Charge Injection",
			"Pulse Data",
			"Analog Display"]
	testFunctionNames = ["get_baseline_periodicselftrigger",
				"get_baseline_periodicexttrigger",
				"get_ThreshLevels",
				"get_leakage_data",
				"get_charge_injection",
				"PulseChannelLoop",
				"AnalogDisplayLoop"]
	testFunctions = [] 

	global buttonVars
	#buttonVars = [] #[len(testList)] # will hold StringVar()
	testButton = [] #[len(testList)] # will hold test checkbuttons

	testID=0
	#print(len(testList))
	global testCheckframe 
	testCheckframe = ttk.Frame(mainframe,padding="10")
	testCheckframe.grid(column=0,row=5)
	row=0	
	for test in testList:
		testFunctions.append(testFunctionNames[testID])
		#print(test)
		buttonVars.append(tk.StringVar())
		#buttonVars[testID].set(testDefaults[testID])
		testButton.append(ttk.Checkbutton(testCheckframe,
			text=test,variable=buttonVars[testID],command=printStatus))
		testButton[testID].grid(column=0,row=row,sticky="W")
		row = row+1
		testID=testID+1

	global textBox
	textBox=tk.Text(mainframe, width = 40, height=10)
	textBox.grid(column=9,row=2,rowspan=10)

	closebutton= ttk.Button(mainframe,text="Quit",command=window.destroy)
	closebutton.grid(column=9,row=99,sticky='E')
	#print("closebutton is at ",str(closebutton))

	SNframe = ttk.Frame(mainframe, padding="5")
	SNframe.grid(column=9,row=0,rowspan=2,sticky='E')
	#SNlabel = ttk.Label(SNframe, text="ASICs to test (1-10)")
	#SNlabel.grid(column=1,row=0)

	global UseTCPIPControlState
	UseTCPIPControlState=tk.StringVar()
	UseTCPIPControlState.set(0)
	UseTCPIPControlBtn= ttk.Checkbutton(SNframe,text="Use TCPIP\nControl",
		variable=UseTCPIPControlState, command=UseTCPIPControl)
	UseTCPIPControlBtn.grid(column=3,row=0,padx=20)

	global LoadHTMLplotsState
	LoadHTMLplotsState=tk.StringVar()
	LoadHTMLplotsState.set(0)
	LoadHTMLplotsBtn= ttk.Checkbutton(SNframe,text="Load HTML\nplot",
		variable=LoadHTMLplotsState) #, command=LoadHTMLplots)
	LoadHTMLplotsBtn.grid(column=3,row=1,padx=20)
	
	global ASICversion  # replace v2b and v2c settings with selector for ASICversion
	ASICversion=tk.StringVar()
	#ASICversion.set('v2b')
	ASICvsnBox=ttk.Combobox(SNframe,text='ASIC version',
							textvariable=ASICversion,
							values=('v2a','v2b','v2c','v2d','v3'),
							width=4,state='readonly')
	ASICvsnBox.bind('<<ComboboxSelected>>' ,NewASICVersion)
	ASICvsnBox.grid(sticky=tk.W,column=4,row=2)
	ASICvsnBox.current(newindex=1)
	ASICvsnlabel = ttk.Label(SNframe,text="ASIC Version:")
	ASICvsnlabel.grid(sticky=tk.SE,column=3, row=2)

	'''
	global v2bState
	v2bState=tk.StringVar()
	v2bState.set(0)
	v2bBtn= ttk.Checkbutton(SNframe,text="v2b ASIC",
		variable=v2bState) #, command=v2b)
	#v2bBtn.grid(column=3,row=2,padx=20)

	global v2cState
	v2cState=tk.StringVar()
	v2cState.set(0)
	v2cBtn= ttk.Checkbutton(SNframe,text="v2c ASIC",
		                variable=v2cState, command=Togglev2c) #, command=v2b)
	#v2cBtn.grid(column=4,row=2,padx=20)
	'''

	global SNAutoIncrement
	SNAutoIncrement=tk.StringVar()
	SNAutoIncrement.set(0)
	SNAutoUpBtn= ttk.Checkbutton(SNframe,text="SN AutoUp",
		variable=SNAutoIncrement, command=SNAutoUp)
	SNAutoUpBtn.grid(column=4,row=0,padx=10)

	global SNfromFile
	SNfromFile=tk.StringVar()
	SNfromFile.set(0)
	SNfromFileBtn= ttk.Checkbutton(SNframe,text="Use SN File",
		variable=SNfromFile, command=UseSNFile)
	SNfromFileBtn.grid(column=5,row=2,padx=10)

	SNUpBtn= ttk.Button(SNframe,text="SN Up",command=SNUp)
	SNUpBtn.grid(column=5,row=0)
	SNDownBtn= ttk.Button(SNframe,text="SN Down",command=SNDown)
	SNDownBtn.grid(column=5,row=1)
	numChipVar = tk.StringVar()
	#numChipVar.set("2")
	#numChipWheel = tk.Spinbox(SNframe,from_=1,to=10,textvariable=numChipVar,command=deploySN)
	#numChipWheel.grid(column=1,row=1,sticky='W')
	#numChipWheel.configure(state="disabled")  # disable multi-chip testing for now
	numChipVar.set("1")
	deploySN()

	try:
		#Initialize the GUI state from the previous run
		#tempstatus = h5py.File("CurrentRun.tmp",mode='r')
		with h5py.File("CurrentRun.tmp",mode='r') as tempstatus:
			dset = tempstatus['CurrentRun']
			ChipSN = dset.attrs['ChipSN']
			testDefaults = dset.attrs['currentTest']
			if len(testDefaults)==0:
				testDefaults = [1,0,0,0,0,0,0]
			testID=0
			for test in testList:
				buttonVars[testID].set(testDefaults[testID])
				testID=testID+1
			UseTCPIPControlState.set(dset.attrs['UseTCPIPControl'])
			LoadHTMLplotsState.set(dset.attrs['LoadHTMLplot'])
			#v2bState.set(dset.attrs['v2bASIC'])
			#v2cState.set(dset.attrs['v2cASIC'])
			SNAutoIncrement.set(dset.attrs['SNAutoUp'])
			ASICvsnBox.set(dset.attrs['ASICversion'])
			# Don't save or restore SNfromFile, since input file needs selection each time
			# tempstatus.close()  No longer needed with with-as
	except IOError as ioe:
		print("Error opening CurrentRun.tmp: ",ioe)
		'''  Set Defaults if CurrentRun.tmp doesn't exist '''
		with h5py.File("CurrentRun.tmp",mode='w') as tempstatus:
			dset = tempstatus.create_dataset("CurrentRun",dtype='i')
			ChipSN='0Z0000'
			dset.attrs['ChipSN']=ChipSN
			testDefaults = [1,0,0,0,0,0,0]
			dset.attrs['currentTest']=testDefaults
			testID=0
			for test in testList:
				buttonVars[testID].set(testDefaults[testID])
				testID=testID+1
			dset.attrs['UseTCPIPControl']='1'
			dset.attrs['LoadHTMLplot']='0'
			#dset.attrs['v2bASIC']=v2bState.get()
			#dset.attrs['v2cASIC']=v2cState.get()
			dset.attrs['SNAutoUp']='0'
			dset.attrs['ASICversion']='v2b'
			# Don't save or restore SNfromFile, since input file needs selection each time
			# tempstatus.close() Not needed with "with" construction
	else: 
		print("I guess that worked." )

	if ChipSN:	mychipIDBox[0].insert(0,ChipSN)
	# seems that deploySN has to happen after first window paint
	# this makes it interactive?
	window.mainloop()
	

def mainish():

	trygui() 
	
	exit()
	
	# this code was moved to runtests for personnel efficiency
	c=init_controller()
	init_board(c)
	chip=init_chips(c)	
	print(chip)	
	
	# Set global threshold
	setGlobalThresh(c,chip,100)

	# Read some Data
	#c.run(1,'test')
	#print(c.reads[-1])

	# Enable analog monitor on one channel
	c.enable_analog_monitor(chip.chip_key,28)
	c.write_configuration(chip.chip_key)
	c.verify_configuration(chip.chip_key,n=2)

	# Turn on periodic_reset
	#chip.config.enable_periodic_reset = 1 # turn on periodic reset
	#c.write_configuration(chip.chip_key)
	#c.verify_configuration(chip.chip_key,n=2)

	# Turn off periodic_reset
	chip.config.enable_periodic_reset = 0 # turn off periodic reset
	# Turn on periodic_reset
	chip.config.enable_periodic_reset = 1 # turn off periodic reset

	# set a really long periodic reset (std=4096)
	#chip.config.periodic_reset_cycles=4096 # 819us
	#chip.config.periodic_reset_cycles=5096 # 1019us
	chip.config.periodic_reset_cycles=100000 # 20ms
	#chip.config.periodic_reset_cycles=1000000 # 200ms
	#chip.config.periodic_reset_cycles=10000000 # 2s

	#set ref vcm  (77 def = 0.54V)
	chip.config.vcm_dac=45
	#set ref vref  ( 219 def = 1.54V)
	chip.config.vref_dac=187
	#set ref current.  (11 for RT, 16 for cryo)
	#chip.config.ref_current_trim=16
	#set ibias_csa  (8 for default, range [0-15])
	#chip.config.ibias_csa=12

	c.write_configuration(chip.chip_key)
	c.verify_configuration(chip.chip_key,n=2)

	# Disable analog monitor (any channel)
	c.disable_analog_monitor(chip.chip_key)
	c.write_configuration(chip.chip_key)
	c.verify_configuration(chip.chip_key,n=2)

	trygui(c,chip)

	#AnalogDisplayLoop(c,chip)
	#get_baseline_periodicexttrigger(c,chip) #ext trig not plugged in 8/20/2020
	#get_baseline_periodicselftrigger(c,chip)
	#get_ThreshLevels(c,chip)

def printStatus():
#	global runPeriodicBaseline
#	global runBaseline
	print("printStatus")
	#print(runPeriodicBaseline.get()," = runPeriodicBaseline")
	# runPeriodicBaseline.set("0")
	# print(runPeriodicBaseline.get()," = runPeriodicBaseline")
	#runPeriodicBaseline.set("1")
	#print(runPeriodicBaseline.get()," = runPeriodicBaseline")
	#print(runBaseline.get()," = runBaseline")
	myiter = 0
	for i in buttonVars:
		print(buttonVars[myiter].get()," = ",testList[myiter])
		myiter=myiter+1

# make the controlling window global. (will probably need a better name)
window = tk.Tk()
#runPeriodicBaseline = tk.StringVar()
#runBaseline = tk.StringVar()
#runPeriodicBaseline.set("1")
#runBaseline.set("0")

testList = []
buttonVars = []
testCheckfram = []

#runPeriodicBaseline="1"
#runBaseline="0"
mainish()

