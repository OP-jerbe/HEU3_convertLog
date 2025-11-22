# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 10:25:15 2024

@author: pwitham
"""

#%% Import modules
import math
#import numpy as np
#import matplotlib.pyplot as plt
#import pandas as pd
#from scipy.optimize import curve_fit
#python -m serial.tools.list_ports
import serial
from datetime import datetime
from datetime import timedelta

logNum = 18
SN = '1060'     #replaced with number found in the log, if present.

#could specify ",buffering: 1" for line buffering?
#fname = 'sn1058log41'
#fname = 'sn1059log8'
fname = 'sn1060log18'
#fname = 'sn1061log56'
#fname = 'sn1110log25'
#fname = 'sn1103log1'

wdir = 'C:/Users/pwitham/Desktop/HEU/HEU3/logDumper/'

timeZoneOffset = 0  #integer hours, added to time stamps.
dateLineOffset = 0

printIt = False    # Print on console?  .txt log is always created.
csvIt = True       # Also create .csv?
commandIt = True   # True = pull the log anew over USB from the HEU.

megs = 1

if commandIt:
#    port = 'COM3' #1110
#    port = 'COM8' #1059
#    port = 'COM6' #1058
    port = 'COM9' #1060

    fname = 'defaultLog'
    ser = serial.Serial(port, 38400, timeout=1)
    print(ser.name + ": %4.0f megs..." % (megs))  #Message on terminal
    ser.write(b'frlog977%04.0f\n'%(megs))
    #ser.write(b'frlog9770001\n')
    reply = ser.readlines(1048576*megs)
    ser.close()             # close port
    ambleState = 0  # 0==printable preamble: command echo, file size.
    #Are we reading the incoming preamble, or the meat, or the postamble?  Don't print the meat.
    #print(reply)  #prints the whole damn mess
    for lines in reply :
        readstr = str(lines.decode("utf-8"))
        if ambleState<2 and readstr[0:6]=='Serial':
            SN = readstr[14:18]
        if readstr=='<\n':
            ambleState = 1   #guts, first line
        if readstr=='>\n':
            ambleState = 3   #postamble, first line
        if ambleState==2:    #guts, the rest
            logOut.writelines(readstr)
        #if ambleState==0 or ambleState==4:
            #print(readstr)
        if ambleState==1:
            ambleState += 1
            fname = 'sn'+SN+f'log{logNum}'
            print(fname)
            logOut = open(wdir+fname+'.txt', 'w')
        if ambleState==3:
            ambleState += 1       
    logOut.close()


logIn  = open(fname+'.txt', 'r')
#+bail gracefully if that file didn't open...
logOut = open(wdir+fname+'out.txt', 'w')  #not appending, wipe previous.
if csvIt:
    csvOut = open(wdir+fname+'.csv', 'w')

mute = 0

logVersion = 2      #1 = the handful from testing 9/5/24 and earlier.
                    #2 switches temperatures to nn.nnC

startLine = 0       #location found for desired start time
endLine = 20000000  #location found for desired end time, or limit to how far to go.

#Ask user for time period or whole log here

#Scan from beginning of log for first and last DT and TI stamps, and seconds.
#convertLog() class is at bottom of file.

###############################################################################################################
#Scan from start, find first DT stamp,
#Scan from start, find last TI stamp, combine for end time.
#Parse each tag and either print a line or add a line to the .CSV file.
def convertLog():
    date = '<none>' #Latest read
    startDate = ''  #first date in log
    endDate = ''    #last date in log
    lastDate = ''   #for detecting change of date
    #newDate = False #is this is a known new date?
    
    time = '<none>'
    startTime = ''
    endTime = ''
    lastTime = ''
    newTime = False
    
    secs = '<none>'
    startSecs =''
    endSecs = ''
    lastSecs = ''
    newSecs = False
    
    linenum = 0
    numThings = 0
    
    #Components of pump states, stored to detect changes:
    lastPumpsOn = -1
    lastPumpsHTshutdown = -1
    lastPumpSelection = -1
    lastPumpsShutdown = -1
    lastP1CurrentHigh = -1.
    lastP2CurrentHigh = -1.
    lastMaxIp1 = -1.
    lastMaxIp2 = -1.
    tag = ''
    date = ''
    time = ''
    secs = ''
    
    #State vars for .csv file writing
    Pon = 0
    PumpsHot = 0
    ePumpSelection = 0
    PumpsShutdown = 0
    P1CurrentHigh = 0
    P2CurrentHigh = 0
    maxIp1 = 0.0
    maxIp2 = 0.0
    fThrot = 0.0
    fInTemp = 0.0
    fOutTemp = 0.0
    fFlow = 0.0
    bIntOn = False
    bRestart = False
    bCold = False
    bPowerdown = False
    bLogClosed = False
    bLeak = False
    fMinFlow = 0.0
    iMaxTemp = 0
    iDissWatts = 0
    iCmds = 0
    iQrys = 0
    iTouches = 0
    ps24V  = ' 0.00'
    ps5V   = ' 0.00'
    ps3p3V = ' 0.00'
    iCpuTemp = 0
    iGlitch0 = 0
    iGlitch1 = 0
    iGlitch2 = 0
    rbtMarker = 0
    dogExpired = 0
    bWDTreboot = 0
    bMysteryRestart = 0
    
    gotIt = False
    txt = ''

    # Parse and convert this non-timestamp log entry, recording in logOut.
    def parseLogEntries(logLine):
        global logIn, logOut, csvOut
        global printIt, csvIt
        nonlocal tag,date,time,secs,gotIt,txt
                
        #for detecting pump state changes
        nonlocal lastPumpsOn, lastPumpsHTshutdown, lastPumpSelection, lastPumpsShutdown
        nonlocal lastP1CurrentHigh, lastP2CurrentHigh, lastMaxIp1, lastMaxIp2
        
        #State variables for csv printing
        nonlocal Pon,PumpsHot,ePumpSelection,PumpsShutdown,P1CurrentHigh,P2CurrentHigh,maxIp1,maxIp2 
        nonlocal fThrot,fInTemp,fOutTemp,fFlow,bIntOn,bRestart,bCold,bPowerdown,bLogClosed,bLeak
        nonlocal fMinFlow,iMaxTemp,iDissWatts,iCmds,iQrys,iTouches,ps24V,ps5V,ps3p3V,iCpuTemp,iGlitch0,iGlitch1,iGlitch2
        nonlocal rbtMarker,dogExpired,bWDTreboot,bMysteryRestart

        
        gotIt = False   #Did this line parse?
        txt = ''
        fluidSpecificHeat = 1796.

        if tag=='PS':              # Pump states.  Many combined things packed in 24b / 8 decimal digits.
            secs = logLine[3:8]
            gotIt = True
            pStates = int(logLine[9:18])    #number conversion
            #  unsigned combined = (unsigned)pumpsOn&0x1;            //bit0
            Pon = pStates&0x1
            if Pon!=lastPumpsOn:
                lastPumpsOn = Pon
                if Pon==1:
                    txt = 'Pumps On                   '
                else:
                    txt = 'Pumps Off                  '
                if printIt: print(txt,f'{date} {time}:{secs}') # ...28 charactors allowed...
                logOut.write(txt+f' {date} {time}:{secs}\n')
            #  combined |= ((unsigned)pumpsHighTempShutdown&0x1)<<1; //bit1
            PumpsHot = (pStates>>1)&0x1
            if PumpsHot!=lastPumpsHTshutdown:
                lastPumpsHTshutdown = PumpsHot
                if PumpsHot==1:
                    txt = 'PUMPS HOT, shut down!      '
                else:
                    txt = 'Pumps not hot.             '     
                if printIt: print(txt,f'{date} {time}:{secs}')
                logOut.write(txt+f' {date} {time}:{secs}\n')
            #  combined |= ((unsigned)pumpSelection&0x3)<<2;         //bit2, bit3
            ePumpSelection = (pStates>>2)&0x3
            if ePumpSelection!=lastPumpSelection:
                lastPumpSelection = ePumpSelection
                if ePumpSelection==0:
                    txt = 'BOTH PUMPS DISABLED!?      '
                elif ePumpSelection==1:
                    txt = 'P.1 Enabled, P.2 DISABLED  '
                elif ePumpSelection==2:
                    txt = 'P.1 DISABLED, P.2 Enabled  '  
                elif ePumpSelection==3:
                    txt = 'Both pumps enabled.        '
                if printIt: print(txt,f'{date} {time}:{secs}')
                logOut.write(txt+f' {date} {time}:{secs}\n')
            #  combined |= ((unsigned)pumpShutdownOverride&0x1)<<4;  //bit4
            PumpsShutdown = (pStates>>4)&0x1
            if PumpsShutdown!=lastPumpsShutdown:
                lastPumpsShutdown = PumpsShutdown
                if PumpsShutdown==1:
                    txt = 'Pumps shutting down        '
                else:
                    txt = 'Pumps running              '
                if printIt: print(txt,f'{date} {time}:{secs}')
                logOut.write(txt+f' {date} {time}:{secs}\n')
            #  combined |= ((unsigned)p1CurrentHigh&0x1)<<5;         //bit5
            P1CurrentHigh = (pStates>>5)&0x1
            if P1CurrentHigh!=lastP1CurrentHigh:
                lastP1CurrentHigh = P1CurrentHigh
                if P1CurrentHigh==1:
                    txt = 'Pump 1 CURRENT HIGH        '
                else:
                    txt = 'Pump 1 current normal.     '
                if printIt: print(txt,f'{date} {time}:{secs}')
                logOut.write(txt+f' {date} {time}:{secs}\n')
            #  combined |= ((unsigned)p2CurrentHigh&0x1)<<6;         //bit6
            P2CurrentHigh = (pStates>>6)&0x1
            if P2CurrentHigh!=lastP2CurrentHigh:
                lastP2CurrentHigh = P2CurrentHigh
                if P2CurrentHigh==1:
                    txt = 'Pump 2 CURRENT HIGH        '
                else:
                    txt = 'Pump 2 current normal.     '
                if printIt: print(txt,f'{date} {time}:{secs}')
                logOut.write(txt+f' {date} {time}:{secs}\n')
            #  combined |= ((unsigned)maxIp1<<7);                    //bits 7-14
            maxIp1 = float((pStates>>7)&0xFF)/10.
            if maxIp1!=lastMaxIp1:
                lastMaxIp1 = maxIp1
                if printIt: print(f'Max pump 1 current {maxIp1:4.1f} A   {date} {time}{secs}')
                logOut.write(f'Max pump 1 current {maxIp1:4.1f} A   {date} {time}:{secs}\n')
            #  combined |= ((unsigned)maxIp2<<15);                   //bits 15-22
            maxIp2 = float((pStates>>15)&0xFF)/10.
            if maxIp2!=lastMaxIp2:
                lastMaxIp2 = maxIp2
                if printIt: print(f'Max pump 2 current {maxIp2:4.1f} A   {date} {time}{secs}')
                logOut.write(f'Max pump 2 current {maxIp2:4.1f} A   {date} {time}:{secs}\n')
            #txt = f'(PS:{pStates:8d})              '
            txt = ''
            # bits 23-25 SPARE in 8 digits
            ### end tag=='PS' #####################################################################################       
        if tag=='TH':              # Pump Throttle change.
            gotIt = True
            throt = logLine[9:15]
            fThrot = float(throt)
            txt = f'Throttle: {fThrot:5.3f}            '
        if tag=='TM':              # Temperature(s) changed.
            gotIt = True
            if logVersion==1:
                inTemp = logLine[9:13]
                outTemp = logLine[13:18]
                fInTemp = float(inTemp)
                fOutTemp = float(outTemp)
                txt = f'Inlet:{fInTemp:4.1f} C, Outlet:{fOutTemp:4.1f} C'
            else:
                inTemp = logLine[9:14]
                outTemp = logLine[14:20]
                fInTemp = float(inTemp)
                fOutTemp = float(outTemp)
                txt = f'Inlet:{fInTemp:5.2f}C, Outlet:{fOutTemp:5.2f}C'
            iDissWatts = int(fFlow/60.*(fInTemp-fOutTemp)*fluidSpecificHeat)
            if mute==1 : txt=''
        if tag=='FL':              # Flow rate changed.
            gotIt = True
            flow = logLine[9:14]
            fFlow = float(flow)
            txt = f'Flow rate: {fFlow:5.2f} l/min     '
            iDissWatts = int(fFlow/60.*(fInTemp-fOutTemp)*fluidSpecificHeat)
            if mute==1 : txt=''
        if tag=='PR':              # Print of log.
            gotIt = True
            txt = 'Log File Read              '
        if tag=='IN':              # Interlock On/Off.
            gotIt = True
            intOn = logLine[9:10]
            bIntOn = bool(int(intOn))
            if bIntOn:
                txt = 'Interlock On               '
            else:
                txt = 'Interlock Off              '
        bRestart = False           # bRestart is only true for one tag's duration.
        bCold = False              # bCold is only true for one tag's duration.
        if tag=='RE':              # Restart
            bRestart = True
            if linenum!=0:         # not a blank log prior to this
                bMysteryRestart = (bPowerdown==False)   #We should have had a logged shutdown before this.  Why?  WDT?
            bWDTreboot = 0         #Will be set with another tag soon if it is a WDT reboot.
            gotIt = True
            cold = logLine[9:10]
            if cold=="C":
                bCold = True
                txt = '\nCOLD RESTART               ' #From power-down or hard reset.
            else:
                txt = '\nWARM RESTART               ' #From brownout.
            lastPumpsOn = -1
            lastPumpsHTshutdown = -1
            lastPumpSelection = -1
            lastPumpsShutdown = -1
            lastP1CurrentHigh = -1.
            lastP2CurrentHigh = -1.
            lastMaxIp1 = -1.
            lastMaxIp2 = -1.

        bPowerdown = False
        if tag=='PD':              # Power going down (voltage<min).
            bPowerdown = True
            gotIt = True
            txt = 'POWER GOING DOWN           '
        bLogClosed = False         # Log bool is only true for one tag's duration.
        if tag=='CL':              # Close of log.
            bLogClosed = True
            bPowerdown = True      # COULD BE A SOFTWARE RELOAD WITH "RELOD" COMMAND, NOTE?
            gotIt = True
            txt = 'LOG CLOSED.                '
        if tag=='LE':              # Leak detected?
            gotIt = True
            leak = logLine[9:10]
            bLeak = bool(int(leak))
            if bLeak:
                txt = 'LEAK detected              '
            else:
                txt = 'No leak                    '
        if tag=='MF':              # Minimum (interlock) flow rate setting
            gotIt = True
            minFlow = logLine[9:14]
            fMinFlow = float(minFlow)
            txt = f'Min flow lim set:{fMinFlow:5.2f} l/m '   
        if tag=='MT':              # Minimum (interlock) temp rate setting
            gotIt = True
            maxTemp = logLine[9:11]
            iMaxTemp = int(maxTemp)
            txt = f'Max temp limit set:{iMaxTemp:2d} C    '   
        if tag=='VE':              # Version numbers
            gotIt = True
            th = logLine[9:11]
            ts = logLine[12:14]
            txt = f'Hardware V{th}, Software V{ts} '    #NOTE: does not sucessfuly produce ints, just strings.
            #txt = f'Hardware V{hV:2d}, Software V{sV:2d} '
            # Now determine and print if the unit rebooted without a shutdown or WDT reboot message:
            if bMysteryRestart:     # Restart without reason!
                logOut.write(f'Restart without Shutdown!   {date} {time}:{secs}\n')     # Extra log entry
        if tag=='DW':              # Dissipated Power, Watts.
            gotIt = True
            #dWatts = logLine[9:13]
            #iDissWatts = int(dWatts)   #logged power, but ignore it as it's behind the values it's created from,
                                        # and just adds double entries.
            #iDissWatts = int(fFlow/60.*(fInTemp-fOutTemp)*fluidSpecificHeat)
            #txt = f'Dissipated Power:{iDissWatts:4d} W    '
            txt = ''  #kill this anyway, it's a duplicate.
        if tag=='IF':              # New valid commands and queries received over the HEU interface(s)
            gotIt = True
            cmds = logLine[9:20]
            iCmds += int(cmds)
            qrys = logLine[20:31]
            iQrys += int(qrys)
            txt = f'Cmds:{iCmds:11d} Qrys:{iQrys:11d}'  
            #txt = '' #IGNORE
        if tag=='TU':              # New screen touches
            gotIt = True
            touches = logLine[9:20]
            iTouches += int(touches)
            txt = f'Touches:{iTouches:11d}'  
        if tag=='SV':              # (power) Supply Voltages.
            gotIt = True
            ps24V  = logLine[9:14]      # 5 of 5 chars
            ps5V   = logLine[16:20]     # 4 of 5 chars
            ps3p3V = logLine[22:26]     # 4 of 5 chars
            #fPs24V = float(ps24V)
            #fPs5V  = float(ps5V)
            #fPs3p3V = float(ps3p3V)
            txt = '24V:'+ps24V+' 5V:'+ps5V+' 3.3V:'+ps3p3V
        if tag=='CT':              # CPU temperature
            gotIt = True
            cpuTemp = logLine[9:13]
            iCpuTemp = float(cpuTemp)
            txt = f'CPU temperature: {iCpuTemp:4.1f} C    '
        #"DB:%05.2f %03d %03d %03d\n", secondz(), fmGlitches0%1000,fmGlitches1%1000,fmGlitches2%1000);
        if tag=='DB':  # Debug print: three counters, 000-999, or any three charactor strings
            gotIt = True
            #print (logLine)
            glitch0  = logLine[9:12]    # 000 000 000\n
            glitch1  = logLine[13:16] 
            glitch2  = logLine[17:20]
            iGlitch0 = int(glitch0)
            iGlitch1 = int(glitch1)
            iGlitch2 = int(glitch2)
            txt = f'Debug 0:{iGlitch0:03d} 1:{iGlitch1:03d} 2:{iGlitch2:03d}    '
            #txt = 'Debug 0:'+glitch0+'  1:'+glitch1+'  2:'+glitch2+'  '
            #txt = ''
        if tag=='WD':              # WDT reboot: type?
            #"WD:%05.2f %1d %1d\n", secondz(), rebootMarker, dog3.expired());
            gotIt = True
            rbtMarker = logLine[9:11]
            dogExpired = logLine[11:12]
            #txt = f'WDT reboot: {rbtMarker:1d} {dogExpired:1d} '
            txt = 'WDT reboot:'+rbtMarker+dogExpired
            bWDTreboot = 1
            bMysteryRestart = False   # Aah.  That's why.
        # Now print that        :
        if gotIt==False and logLine!='\n' and logLine!='':
            txt = f'Unrecognizable tag: {logLine}'
            if printIt:     #Comment out for verbose run
              print(f'Line {linenum} '+txt)
        else:
            if (mute==0) & (txt!=''):
                if printIt: print(txt,f'{date} {time}{lastSecs}')
                logOut.write(txt+f' {date} {time}:{secs}\n')
            #if csvIt:
            #    csvOut.write('')
        # end parseLogEntries
        
    if csvIt: 
        # Write the HEADER line with the column names         #248 characters!
        csvOut.write('Time,')
        csvOut.write('Pon,PumpsHot,ePumpSelection,PumpsShutdown,P1CurrentHigh,P2CurrentHigh,maxIp1,maxIp2,')
        csvOut.write('fThrot,fInTemp,fOutTemp,fFlow,bIntOn,bRestart,bCold,bPowerdown,bLogClosed,bLeak,fMinFlow,')
        #csvOut.write('iMaxTemp,iDissWatts,newCmds,newQrys,ps24V,ps5V,ps3p3V,iCpuTemp,Glitch0,Glitch1,Glitch2,')
        csvOut.write('iMaxTemp,iDissWatts,newCmds,newQrys,newTouches,ps24V,ps5V,ps3p3V,iCpuTemp,iGlitch0,iGlitch1,iGlitch2,')
        csvOut.write('bWDTreboot,bMysteryRestart\n')
           
#Scan from start, find location of start time/date,
#  danger: If TI is first, use Date from DT (-1 if midnight) and time from TI.
#  specified start doesn't exist? Complain, restart.
#Convert each line.
#Continue forward, end when desired stop time is reached.
    linenum = 0
    extraLines = 0
    csvLine = ''
    lastDateDup = ''
    #lastTimeDup = ''
    #lastSecsDup = ''
    fSecs = 0.
    #fSecsPrev = 0.
    fTimeSecs = 0.
    previousDT = datetime.strptime('01/01/00', '%m/%d/%y')

    while linenum<startLine:          # Move to start line,
        logLine = logIn.readline()
        linenum += 1
    while linenum<endLine:            # Then scan log by lines, finding time and date stamps,
                                      #  and parse the other tags using parseLogEntries.
        if printIt: print(linenum)    #   (enable to find bad point in log)
        logLine = logIn.readline()
        if logLine=='':
            break
        linenum += 1
        gotStamp = False
        #Extract date and time stamps, combine.
        tag = logLine[:2]
        #gotBAD = False
        
        if tag=='DT':              # Update MM/DD/YY HH:MM:SS
            dateQ = logLine[3:6]
            if dateQ!='BAD':
                date = logLine[3:11]
                #gotBAD = True
                #print('!')
            #else:  # unchanged from previous?  23 times out of 24...
                #date = logLine[3:8]     #BAD 1 or BAD 2
            time = logLine[12:17]
            #print (time)

            timeDT = datetime.strptime(time, '%H:%M')
            #print(timeDT.hour, timeDT.minute)
            dateDT = datetime.strptime(date, '%m/%d/%y')
            if timeDT.hour==0:
                if dateDT.day==previousDT.day:
                    #increment date by one day!
                    dateDT += timedelta(days=1)
            if dateDT<previousDT :
                dateDT = previousDT     #REPLACE with later, previous date!
            #print(dateDT.month, dateDT.day , dateDT.year, timeDT.hour)
            
            if timeZoneOffset!=0:    #Add time zone offset:  >REWRITE ALL TO USE DATETIME<
                hour = int(time[0:2]) + timeZoneOffset
                minute = int(time[3:5])
                day = int(date[3:5])
                month = int(date[0:2])
                year = int(date[6:8])
                if hour>23:     #positive shift in date
                    hour -= 24
                    day += 1    #FAIL AT MONTH BOUNDARY!
                else:
                    if hour<0:  #negative shift in date
                        hour += 24
                        day -= 1    #FAIL AT MONTH BOUNDARY!
                time = f'{hour:02d}:{minute:02d}'   #re-form the time& date strings.
            if dateLineOffset!=0 or timeZoneOffset!=0:
                day += dateLineOffset   #FAIL AT MONTH BOUNDARY!
                date = f'{month:02d}/{day:02d}/{year:02d}'

            secs = logLine[18:23]
            if startDate=='':
                startDate = date
            endDate = date
            if time!='':
                newTime = True
                if startTime=='':
                    startTime = time
                    endTime = time
            if secs!='':
                lastSecs = secs
                if startSecs=='':
                    startSecs = secs
                    if mute==0 :        #This line isn't in the .csv file in any case:
                        print('\nStart:',startDate, startTime, startSecs)
                endSecs = secs
                newSecs = True
            gotStamp = True     # This log line is a time stamp?
            previousDT = dateDT     #Remember properly sequential date
    
        # Update H:M  (always preceeds another log entry, which has seconds)
        if tag=='TI':
            time = logLine[3:8]
            
            if timeZoneOffset!=0:    #Add time zone offset:
                hour = int(time[0:2]) + timeZoneOffset
                minute = int(time[3:5])
                #day = int(date[3:5])       #DATE HAS ALREADY BEEN ADJUSTED IN DT TAG PROCESS
                #month = int(date[0:2])
                #year = int(date[6:8])
                if hour>23:     #positive shift in date
                    hour -= 24
                #    day += 1    #FAIL AT MONTH BOUNDARY!
                #else:
                #    if hour<0:  #negative shift in date
                #        hour += 24
                #        day -= 1    #FAIL AT MONTH BOUNDARY!
                #date = f'{month:02d}/{day:02d}/{year:02d}'
                time = f'{hour:02d}:{minute:02d}'   #re-form the time string.

            if startTime=='' :      #this may never happen... DT stamp comes first.
                startTime = time
            endTime = time
            gotStamp = True
            if time!=lastTime :     #Detect changed time and print that.
                newTime = True
                lastTime = time
            newSecs = False
    
        if gotStamp==False :        #Other log entries: Update :secs.hundredths
            numThings+=1
            secs = logLine[3:8]
            if secs!='':
                if secs!=lastSecs:
                    if startSecs=='':
                        startSecs = secs
                    endSecs = secs
                newSecs = True
                lastSecs = secs
            parseLogEntries(logLine) #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # Ok, did we get a time stamp or a parsable tag with something else? 
        if csvIt and date!='':
            #if time == '14:25': print(gotStamp,gotIt,txt,date,time,secs)
            if (gotStamp and newSecs) or (gotIt and txt!='' and newSecs):  #blank txt is a flag to mute this log entry
#Did we get a "BAD n" DateTime stamp?  Calculate the next hour and use that.
                
                #Did we log an earlier date stamp after a later one?
                #if (int(date[6:8]==0)) or (int(date[0:2]==0)) or (int(date[3:5]==0)):
                #    print ('Ble?', date[6:8], date[0:2], date[3:5])
                #if (date!='') and (lastDate!=''):
                #    yearD  = int(date[6:8]) - int(lastDate[6:8])
                #    monthD = int(date[0:2]) - int(lastDate[0:2])
                #    dayD   = int(date[3:5]) - int(lastDate[3:5])
                #    if (yearD<0) or (yearD==0 and monthD<0) or (yearD==0 and monthD==0 and dayD<0):
                #         print ('Bleh! ', date, lastDate)

                fTimeSecsPrev = fTimeSecs
                fSecs = float(secs)
                fMins = float(time[3:6])
                fHrs = float(time[0:2])
                fTimeSecs = fHrs*3600+fMins*60+fSecs
                #print (fSecs)
                if date==lastDateDup and (fTimeSecs-fTimeSecsPrev)>0.02:
                #if date==lastDateDup and time==lastTimeDup and secs==lastSecsDup:
                    if math.floor(fSecs*100.)!=0:                        
                        fLeadingEdge = (math.floor(fSecs*100.)-1.)/100.
                    else:
                        fLeadingEdge = (math.floor(fSecs*100.)   )/100.
                    csvOut.write(f'{date} {time}:{fLeadingEdge:05.2f},' + csvLine)   #duplicate previous values
                    extraLines+=1
                #    print ('!')
                csvLine =  (f'{Pon},{PumpsHot},{ePumpSelection},{PumpsShutdown},')
                csvLine += (f'{P1CurrentHigh},{P2CurrentHigh},{maxIp1},{maxIp2},')
                csvLine += (f'{fThrot:05.3f},{fInTemp:5.2f},{fOutTemp:5.2f},{fFlow:5.2f},')
                csvLine += (f'{int(bIntOn)},{int(bRestart)},{int(bCold)},{int(bPowerdown)},{int(bLogClosed)},{int(bLeak)},')
                csvLine += (f'{fMinFlow:4.2f},{iMaxTemp},{iDissWatts},{iCmds},{iQrys},{iTouches},{ps24V},{ps5V},{ps3p3V},{iCpuTemp},')
                csvLine += (f'{iGlitch0},{iGlitch1},{iGlitch2},{bWDTreboot},{int(bMysteryRestart)}\n')
                csvOut.write(f'{date} {time}:{secs},' + csvLine)
                lastDateDup = date
                #lastTimeDup = time
                #lastSecsDup = secs
   
        if date!=lastDate:
            lastDate = date
            #newDate = True
        if newSecs==True & newTime==True:
            newSecs = False
            newTime = False
            #newDate = False
                     
    #print / return limits.
    if endDate :          #This line isn't in the .csv file in any case:
            print(  'End  :', endDate, endTime, endSecs)
    print(linenum,'lines +',extraLines,'added')
    
    #blah = input("Enter blah:")
    logIn.close()
    logOut.close()
    if csvIt: csvOut.close()

convertLog()

