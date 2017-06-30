#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2014, NewAE Technology Inc
# All rights reserved.
#
# Authors: Colin O'Flynn
#
# Find this and more at newae.com - this file is part of the chipwhisperer
# project, http://www.assembla.com/spaces/chipwhisperer
#
#    This file is part of chipwhisperer.
#
#    chipwhisperer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    chipwhisperer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with chipwhisperer.  If not, see <http://www.gnu.org/licenses/>.
#=================================================

from chipwhisperer.common.api.CWCoreAPI import CWCoreAPI  # Import the ChipWhisperer API
from chipwhisperer.common.scripts.base import UserScriptBase
from stlink_programmer import STLinkProgrammer
import time
import sys


FW_FILE = r"..\fw_build\fw\GCC_AES_CW308_STM32F2_CRYPTO_TARGET=MBEDTLS_OPT=0_.hex"

class UserScript(UserScriptBase):
    _name = "ChipWhisperer-Lite: AES SimpleSerial on XMEGA"
    _description = "SimpleSerial with Standard Target for AES (XMEGA)"

    def __init__(self, api):
        super(UserScript, self).__init__(api)

    def run(self):

        st = STLinkProgrammer()

        # User commands here
        self.api.setParameter(['Generic Settings', 'Scope Module', 'ChipWhisperer/OpenADC'])
        self.api.setParameter(['Generic Settings', 'Target Module', 'Simple Serial'])
        self.api.setParameter(['Generic Settings', 'Trace Format', 'ChipWhisperer/Native'])
        self.api.setParameter(['Simple Serial', 'Connection', 'NewAE USB (CWLite/CW1200)'])
        self.api.setParameter(['ChipWhisperer/OpenADC', 'Connection', 'NewAE USB (CWLite/CW1200)'])
                
        self.api.connect()
        
        # Example of using a list to set parameters. Slightly easier to copy/paste in this format
        lstexample = [['CW Extra Settings', 'Trigger Pins', 'Target IO4 (Trigger Line)', True],
                      ['CW Extra Settings', 'Target IOn Pins', 'Target IO1', 'Serial RXD'],
                      ['CW Extra Settings', 'Target IOn Pins', 'Target IO2', 'Serial TXD'],
                      ['OpenADC', 'Clock Setup', 'CLKGEN Settings', 'Desired Frequency', 7370000.0],
                      ['CW Extra Settings', 'Target HS IO-Out', 'CLKGEN'],
                      ['OpenADC', 'Clock Setup', 'ADC Clock', 'Source', 'CLKGEN x4 via DCM'],
                      ['OpenADC', 'Trigger Setup', 'Total Samples', 10000],
                      ['OpenADC', 'Trigger Setup', 'Offset', 0],
                      ['OpenADC', 'Gain Setting', 'Setting', 45],
                      ['OpenADC', 'Trigger Setup', 'Mode', 'rising edge'],
                      # Final step: make DCMs relock in case they are lost
                      ['OpenADC', 'Clock Setup', 'ADC Clock', 'Reset ADC DCM', None],
                      ]
        
        # Download all hardware setup parameters
        for cmd in lstexample: self.api.setParameter(cmd)


        ##### HARDWARE SETUP
        #Check STM32F target requested
        temp = FW_FILE.split("_")
        target_device = "UNKNOWN"
        for t in temp:
            if "STM32F" in t:
                target_device = t
                break

        #Confirm we are using correct device
        actual_device = st.check_device()
        if target_device not in actual_device:
            raise IOError("ERROR: requested firmware has target = %s, detected board  = %s" % (target_device, actual_device))

        #Program device
        st.program(FW_FILE)

        #Toggle power
        self.api.setParameter(['CW Extra Settings', 'Target Power State', False])
        time.sleep(0.1)
        self.api.setParameter(['CW Extra Settings', 'Target Power State', True])
        time.sleep(0.1)

        self.api.setParameter(['Generic Settings', 'Auxiliary Module', 'Record Length of Trigger/Trace'])

        ##### Check encryption length
        self.api.capture1()
        self.api.capture1()
        time.sleep(0.05)
        trig_len = self.api.getParameter(['OpenADC', 'Trigger Setup', 'Trigger Active Count'])

        if trig_len < 1000:
            raise IOError("ERROR: Trigger appears to have failed (len = %d)"%trig_len)

        self.api.setParameter(['OpenADC', 'Trigger Setup', 'Total Samples', trig_len])
        print trig_len

        # Capture a set of traces and save the project
        # self.api.captureM()
        # self.api.saveProject("../../../projects/test.cwp")

        #sys.exit()


if __name__ == '__main__':
    import chipwhisperer.capture.ui.CWCaptureGUI as cwc         # Import the ChipWhispererCapture GUI
    #from chipwhisperer.common.utils.parameter import Parameter  # Comment this line if you don't want to use the GUI
    #Parameter.usePyQtGraph = True                               # Comment this line if you don't want to use the GUI
    api = CWCoreAPI()                                           # Instantiate the API
    app = cwc.makeApplication("Capture")                        # Change the name if you want a different settings scope
    #gui = cwc.CWCaptureGUI(api)                                 # Comment this line if you don't want to use the GUI
    api.runScriptClass(UserScript)                              # Run the User Script (executes "run()" by default)
    #app.exec_()                                                 # Comment this line if you don't want to use the GUI