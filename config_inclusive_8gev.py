import os
import sys
import json

from LDMX.Framework import ldmxcfg
from LDMX.SimCore import simulator as sim
from LDMX.SimCore import generators as gen

thispassname = 'test'

p = ldmxcfg.Process(thispassname)

mySim = sim.simulator( "inclusive_8gev" )
mySim.setDetector( 'ldmx-det-v14-8gev' )

mySim.generators.append( gen.single_8gev_e_upstream_tagger() )
mySim.beamSpotSmear = [20.,80.,0.] # will be same as 4GeV?
mySim.description = '8 GeV inclusive bkg sample Simulation'

p.sequence = [ mySim ]

##################################################################
# Below should be the same for all sim scenarios
#
#Set run parameters. These are all pulled from the job config
#


#p.run = int(os.environ['LDMX_RUN_NUMBER'])
#p.maxEvents = int(os.environ['LDMX_NUM_EVENTS'])

p.run = int(sys.argv[1])
nElectrons = 1
beamEnergy = 8.0; #in GeV
p.maxEvents = int(sys.argv[2])
p.maxTriesPerEvent = int(sys.argv[3])

#p.histogramFile = 'hist_8Gev_inclusive.root'



import LDMX.Ecal.EcalGeometry
import LDMX.Ecal.ecal_hardcoded_conditions
import LDMX.Hcal.HcalGeometry
import LDMX.Hcal.hcal_hardcoded_conditions
import LDMX.Ecal.digi as eDigi
import LDMX.Ecal.vetos as eVetos
import LDMX.Hcal.digi as hDigi
from LDMX.Hcal import hcal

from LDMX.TrigScint.trigScint import TrigScintDigiProducer
from LDMX.TrigScint.trigScint import TrigScintClusterProducer
from LDMX.TrigScint.trigScint import trigScintTrack

from LDMX.Recon.electronCounter import ElectronCounter
from LDMX.Recon.simpleTrigger import TriggerProcessor
from LDMX.DQM import dqm

#and reco...

#TS digi + clustering + track chain. downstream pad removed to far upstream, but only in v14; left where it was in v12
#ts_digis = [
#        TrigScintDigiProducer.pad1(),
#        TrigScintDigiProducer.pad2(),
#       TrigScintDigiProducer.pad3(),
#        ]
#for d in ts_digis :
#    d.randomSeed = 1

tsDigisDown = TrigScintDigiProducer.pad1()
tsDigisTag = TrigScintDigiProducer.pad2()
tsDigisUp = TrigScintDigiProducer.pad3()
tsDigisDown.randomSeed = 1
tsDigisTag.randomSeed = 1
tsDigisUp.randomSeed = 1


# electron counter so simpletrigger doesn't crash
count = ElectronCounter(1,'ElectronCounter')
count.input_pass_name = thispassname
count.use_simulated_electron_number = True

##trigger setup, no skim ? 
#simpleTrigger = TriggerProcessor('simpleTrigger')
#simpleTrigger.start_layer = 0
#simpleTrigger.input_pass = thisPassName


#hcal.HcalVetoProcessor ? 

tsClustersDown = TrigScintClusterProducer.pad1()
tsClustersTag = TrigScintClusterProducer.pad2()
tsClustersUp = TrigScintClusterProducer.pad3()

tsClustersDown.input_collection = tsDigisDown.output_collection
tsClustersTag.input_collection = tsDigisTag.output_collection
tsClustersUp.input_collection = tsDigisUp.output_collection


#make sure to pick up the right pass
tsClustersTag.input_pass_name = thispassname
tsClustersUp.input_pass_name = tsClustersTag.input_pass_name
tsClustersDown.input_pass_name = tsClustersTag.input_pass_name

trigScintTrack.input_pass_name = thispassname
trigScintTrack.seeding_collection = tsClustersTag.output_collection

#calorimeters
ecalDigi = eDigi.EcalDigiProducer('ecalDigi')
ecalReco = eDigi.EcalRecProducer('ecalRecon')
ecalVeto = eVetos.EcalVetoProcessor('ecalVetoBDT')
hcalDigi = hDigi.HcalDigiProducer('hcalDigi')
hcalReco = hDigi.HcalRecProducer('hcalRecon')
hcalVeto = hcal.HcalVetoProcessor('hcalVeto')

p.sequence.extend([ecalDigi,
                   ecalReco,
                   ecalVeto,
                   hcalDigi,
                   hcalReco,
                   hcalVeto,
                   tsDigisTag,
                   tsDigisUp,
                   tsDigisDown,
                   tsClustersTag,
                   tsClustersUp,
                   tsClustersDown,
                   trigScintTrack,
                   count,
                   TriggerProcessor('trigger'),
                   #dqm.PhotoNuclearDQM(verbose=False),
                   ]
                  #+ dqm.all_dqm
                  )
 
#p.keep = ["drop MagnetScoringPlaneHits", "drop TrackerScoringPlaneHits", "drop HcalScoringPlaneHits"] #?
#p.keep = ["drop MagnetScoringPlaneHits", "keep TrackerScoringPlaneHits", "keep TargetScoringPlaneHits", "drop HcalScoringPlaneHits"] #?


p.outputFiles = ['events_8gev_10k.root']
#p.histogramFile = 'hist_8gev.root'


p.termLogLevel = 2
logEvents = 200
if (p.maxEvents < logEvents):
   logEvents = p.maxEvents

p.logFrequency = int(p.maxEvents/logEvents)

p.pause()
