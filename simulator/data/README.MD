# Dir of input and output data

Examples:
- dev-original-twitter-data.dict: original file from TwitterMonitor crawlers.
Used in SpatiotemporalTraceExporter. The format is a string version of dicts
from Python, so must be read with eval function.
- dev-1-twitter.json: trace resulted from SpatiotemporalTraceExporter,
usually groups samples from the same week.
- dev-edges-2016-17.json: outputfile of the simulator. It describes the estimated
encounters through the samples provided.
