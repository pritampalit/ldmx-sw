from LDMX.Framework import ldmxcfg

p = ldmxcfg.Process('8gevinclusive')

from LDMX.DQM import dqm
val = dqm.SampleValidation('SampleValidation')

p.sequence=[val]

import sys
p.inputFiles=[sys.argv[2]]

p.histogramFile=sys.argv[1]

p.pause()
