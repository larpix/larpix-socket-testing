import larpix
import larpix.io
#from base import utility_base
#from base import pacman_base
import time

def read(c,key,param):
    c.reads = []
    c.read_configuration(key,param,timeout=0.01)
    message = c.reads[-1]
    for msg in message:
        if not isinstance(msg,larpix.packet.packet_v2.Packet_v2):
            continue
        if msg.packet_type not in [larpix.packet.packet_v2.Packet_v2.CONFIG_READ_PACKET]:
            continue
        print(msg)

def conf_root(c,cm,cadd,iog,iochan):
    I_TX_DIFF=0
    TX_SLICE=15
    R_TERM=2
    I_RX=8
    #REF_CURRENT_TRIM = 0
    REF_CURRENT_TRIM = 15

    c.add_chip(cm,version='2b')
    #  - - default larpix chip_id is '1'
    default_key = larpix.key.Key(iog, iochan, 1) # '1-5-1'
    c.add_chip(default_key,version='2b') # TODO, create v2c class
    #  - - rename to chip_id = cm
    c[default_key].config.chip_id = cadd
    c.write_configuration(default_key,'chip_id')
    #  - - remove default chip id from the controller
    c.remove_chip(default_key)
    #  - - and add the new chip id
    print(cm)

    c[cm].config.chip_id=cadd

    #if iochan == 8:
    if False:
        print('maximum ref current trim')
        # krw, try increasing reference current for cold ops
        c[cm].config.ref_current_trim=REF_CURRENT_TRIM
        c.write_configuration(cm, 'ref_current_trim')
        c[cm].config.current_monitor_bank0=[0,0,0,1]
        c.write_configuration(cm, 'current_monitor_bank0')
        c[cm].config.ibias_csa=8
        c.write_configuration(cm, 'ibias_csa')


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
    
def main():

    ###########################################
    IO_GROUP = 1
    PACMAN_TILE = 2
    #IO_CHAN = (1+(PACMAN_TILE-1)*4)
    IO_CHAN = 5
    #VDDA_DAC= 44500 # ~1.8 V
    #VDDD_DAC = 28500 # ~1.1 V
    VDDA_DAC = 44500
    VDDD_DAC = 30000
    RESET_CYCLES = 300000 #5000000

    REF_CURRENT_TRIM=0
    ###########################################

    # create a larpix controller
    c = larpix.Controller()
    c.io = larpix.io.PACMAN_IO(config_filepath='/home/apdlab/larpixv2/configs/io/pacman20.json', relaxed=True)
    io_group=IO_GROUP
    pacman_version='v1rev4'
    pacman_tile=[PACMAN_TILE]
    chip=11
    cadd=12

    do_power_cycle = True

    if do_power_cycle:
        #disable pacman rx uarts
        print('enable pacman power')
        bitstring = list('00000000000000000000000000000000')
        print(int("".join(bitstring),2))
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
        

        print('reset the larpix for n cycles',RESET_CYCLES)
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
        print('enable tilereg 0x10 , ', tile_enable_val)
        #readback=pacman_base.power_readback(c.io, io_group, pacman_version,pacman_tile)

        #   - toggle reset bit
        RESET_CYCLES = 50000
        c.io.set_reg(0x1014,RESET_CYCLES,io_group=IO_GROUP)
        clk_ctrl = c.io.get_reg(0x1010, io_group=IO_GROUP)
        c.io.set_reg(0x1010, clk_ctrl|4, io_group=IO_GROUP)
        c.io.set_reg(0x1010, clk_ctrl, io_group=IO_GROUP)
        time.sleep(0.01)



    chip11_key=larpix.key.Key(IO_GROUP,IO_CHAN,11)
    conf_root(c,chip11_key,11,IO_GROUP,IO_CHAN)    
    read(c,chip11_key,'enable_piso_downstream')
   
    while True:
        print('loop')
        c.reads = []
        c.read_configuration(chip11_key,'chip_id')
        message = c.reads[-1]
        for msg in message:
            print(msg)
            if not isinstance(msg,larpix.packet.packet_v2.Packet_v2):
                continue
            if msg.packet_type not in [larpix.packet.packet_v2.Packet_v2.CONFIG_READ_PACKET]:
                continue
            if msg.chip_id <255:
                print(msg.chip_id)
        c.write_configuration(chip11_key)
        verified,returnregisters=c.verify_configuration(chip11_key)
        print(verified,returnregisters)

        time.sleep(0.1)
    return c, c.io


if __name__=='__main__':
    main()

