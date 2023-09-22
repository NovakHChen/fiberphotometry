"""
Set lenght of recording for running fiberphotometry experiments. 
This is a modified version of the example script from TDT.
This def does not work as expected. the recording time is 2x
longer than TOTAL_TIME.
"""
#!/usr/bin/env python
# coding: utf-8

# # Run Experiment For Set Duration
# 
# This examples shows how to use Python to control the Synapse mode and
# monitor recording status. <br />
# This uses the 'ExperimentSetTime' example experiment, but it could run with any
# experiment.
# 
# ## Housekeeping
# 
# Import tdt library for SynapseAPI, and Python's built-in time library so we can add a pause
# 
import time
import tdt


# ## Setup
# 
# Choose which experiment to run and the duration. It could be anything.
# This example uses a simple experiment with just a Tick store.
# To see full list of available experiments use syn.getKnownExperiments()


EXPERIMENT = 'ExperimentSetTime'
TOTAL_TIME = 30

# Connect to Synapse
syn = tdt.SynapseAPI()

# Set your experiment
syn.setCurrentExperiment(EXPERIMENT)


# Runtime

# Set the system to 'Preview' mode
syn.setModeStr('Preview')

# Wait five seconds to give 'getSystemStatus' time to update internally
time.sleep(5)


# ## Main Loop

currTime = 0
prevTime = 0

# Poll the system status until it reaches the desired state
while currTime < TOTAL_TIME:

    # Add any additional API controls here
    currTime = syn.getSystemStatus()['recordSecs']
    if prevTime != currTime:
        print(f'Current elapsed time: {currTime}s')

    prevTime = currTime


# Our desired elapsed time has passed, switch to Idle mode

syn.setModeStr('Idle')
print('done')
