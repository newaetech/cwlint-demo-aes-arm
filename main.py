"""
main.py
This is the main control script for the SC-Lint ARM AES demo.

Pre-requirements:
 - ChipWhisperer Lite/Pro and CW308 UFO board connecting to computer
 - SC-Lint server already running

Step-by-step:
1. Capture power traces 
  a. Connect to ChipWhisperer
  b. Program firmware onto STM32 target
  c. Prepare scope settings
  d. Capture 1 and set capture length appropriately
  e. Capture Many
2. Run analysis on power traces
  a. Create and run SC-Lint project
  b. Wait for analysis to finish
  c. Generate test report
3. Repeat 1-2 for all firmware files
4. Generate summary report
"""

from chipwhisperer.common.api.CWCoreAPI import CWCoreAPI  # Import the ChipWhisperer API
from chipwhisperer.common.scripts.base import UserScriptBase
from cwcapture_example_scripts.stlink_programmer import STLinkProgrammer
import datetime
import os.path
import subprocess
import time
import sys

# List of firmware files to analyze.
fw_path = "fw_build/fw"
fw_fnames = [
    fw for fw in os.listdir(fw_path) if 'STM32F0' in fw
]
#fw_fnames = [
#    "GCC_AES_CW308_STM32F2_CRYPTO_TARGET=MBEDTLS_OPT=0_.hex",
#]

# SC-Lint config file to use
# TODO: use full AES test or TVLA
sclint_config = "C:/Users/greg/Documents/autoanalysis/restapi/config/aes128_simple.cfg"

# Path to SC-Lint client
sclint_path = "../autoanalysis/restapi/client/client.py"

# SC-Lint server location
sclint_server = "http://127.0.0.1:5000"

# CW project path
cwp_path = "output/cwprojects"

# Number of traces per firmware
num_traces = 2000

# Report path
report_path = "output/reports"

def program_stm(fw_fname):
    """
    Program an STM32F device with firmware.
    
    Raises an IOError if target in filename doesn't match connected device.
    """
    
    st = STLinkProgrammer("stlink_cli\ST-LINK_CLI.exe")
    
    temp = fw_fname.split("_")
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
    st.program(fw_fname)

def setup_chipwhisperer(api):
    """
    One-time setup for the ChipWhisperer - gets the settings ready once.
    """
    
    # Connect to CW
    api.setParameter(['Generic Settings', 'Scope Module', 'ChipWhisperer/OpenADC'])
    api.setParameter(['Generic Settings', 'Target Module', 'Simple Serial'])
    api.setParameter(['Generic Settings', 'Trace Format', 'ChipWhisperer/Native'])
    api.setParameter(['Simple Serial', 'Connection', 'NewAE USB (CWLite/CW1200)'])
    api.setParameter(['ChipWhisperer/OpenADC', 'Connection', 'NewAE USB (CWLite/CW1200)'])
    api.setParameter(['Generic Settings', 'Acquisition Settings', 'Key/Text Pattern', 'CRI T-Test'])
            
    api.connect()
    
    # Load parameters
    lstexample = [['CW Extra Settings', 'Trigger Pins', 'Target IO4 (Trigger Line)', True],
                  ['CW Extra Settings', 'Target IOn Pins', 'Target IO1', 'Serial RXD'],
                  ['CW Extra Settings', 'Target IOn Pins', 'Target IO2', 'Serial TXD'],
                  ['OpenADC', 'Clock Setup', 'CLKGEN Settings', 'Desired Frequency', 7370000.0],
                  ['CW Extra Settings', 'Target HS IO-Out', 'CLKGEN'],
                  ['OpenADC', 'Clock Setup', 'ADC Clock', 'Source', 'CLKGEN x4 via DCM'],
                  ['OpenADC', 'Trigger Setup', 'Total Samples', 10000],
                  ['OpenADC', 'Trigger Setup', 'Offset', 0],
                  ['OpenADC', 'Gain Setting', 'Setting', 50],
                  ['OpenADC', 'Trigger Setup', 'Mode', 'rising edge'],
                  ['OpenADC', 'Clock Setup', 'ADC Clock', 'Reset ADC DCM', None],
                  ]
    
    for cmd in lstexample: api.setParameter(cmd)
    
def capture_project(api, fw_fname, cwp_fname):
    """
    Load fw onto target device and capture traces into cwp project
    """
    program_stm(fw_fname)

    #Toggle power
    api.setParameter(['CW Extra Settings', 'Target Power State', False])
    time.sleep(0.1)
    api.setParameter(['CW Extra Settings', 'Target Power State', True])
    time.sleep(0.1)

    api.setParameter(['Generic Settings', 'Auxiliary Module', 'Record Length of Trigger/Trace'])

    ##### Check encryption length
    api.capture1()
    api.capture1()
    time.sleep(0.05)
    trig_len = api.getParameter(['OpenADC', 'Trigger Setup', 'Trigger Active Count'])
    if trig_len < 1000:
        raise IOError("ERROR: Trigger appears to have failed (len = %d)"%trig_len)
    api.setParameter(['OpenADC', 'Trigger Setup', 'Total Samples', trig_len])
    api.setParameter(['Generic Settings', 'Acquisition Settings', 'Number of Traces', num_traces])
    
    # Record traces
    api.newProject()
    api.saveProject(cwp_fname)
    api.captureM()
    api.saveProject(cwp_fname)
    
if __name__ == "__main__":
    # Record timestamp for labelling output
    run_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Get ChipWhisperer API ready
    import chipwhisperer.capture.ui.CWCaptureGUI as cwc
    app = cwc.makeApplication("Capture")
    api = CWCoreAPI()
    
    # Set up the ChipWhisperer
    setup_chipwhisperer(api)

    for fw_fname in fw_fnames:
        print "Testing firmware file %s..." % fw_fname
        
        # Run capture script
        print "Capturing power traces..."
        base_fname = "%s-%s" % (run_timestamp, fw_fname)
        fw_fname_full = os.path.join(fw_path, fw_fname)
        cwp_fname = os.path.join(cwp_path, "%s.cwp" % base_fname)
        capture_project(
            api, 
            os.path.abspath(fw_fname_full), 
            cwp_fname
        )
        print "Finished capturing traces into project %s" % cwp_fname
        
        # Run SC-Lint analysis
        print "Running analysis..."
        run_output = subprocess.check_output([
            "python", 
            sclint_path, 
            "run", 
            "--cwproject=%s" % os.path.abspath(cwp_fname), 
            "--config=%s" % sclint_config,
            sclint_server
        ])
        
        # Get project URI from run output
        print run_output
        goal_str = "Project created at"
        for line in run_output.split('\n'):
            if goal_str in line:
                print line
                project_uri = line.split(goal_str)[1].strip()
                break
        
        # Wait for analysis to finish
        print "Analysis setup complete: project running at %s" % project_uri
        print "Waiting for analysis to complete..."
        subprocess.call([
            "python",
            sclint_path,
            "status",
            "--block",
            project_uri
        ])
        
        # Generate report
        print "Analysis complete."
        print "Generating report..."
        report_fname = os.path.join(report_path, "%s.html" % base_fname)
        subprocess.call([
            "python", 
            sclint_path, 
            "result", 
            "--html", 
            os.path.abspath(report_fname), 
            project_uri
        ])
        
        print "Finished firmware file %s" % fw_fname
        
    print "Finished analyzing all firmware"
