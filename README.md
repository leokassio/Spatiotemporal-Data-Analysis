# Spatiotemporal Data Analysis

![alt text](http://data.whicdn.com/images/69304651/large.gif "Welcome!")

(This is a work in progress)

Set of tools for exploratory data analysis using Twitter, Instagram and Foursquare data.

### Data Acquisition
* TwitterMonitor.py: module to define the basic functions used by TwitterMonitor crawlers. Actually, it includes banner and configuration loaders.
* TwitterMonitor.cfg
* TwitterMonitor.cfg: the configuration file for Twitter crawlers. It defines the authentication dredentials, bounding boxes, hashtags among other parameters. It uses the Python SafeConfigParser to manage the configurations.
* TwitterMonitorGeolocation: crawler to capture the tweets with precise geolocation (samples with with GPS coords - latitude and longitude) determined by a bounding box, but independently of hashtags.
* TwitterMonitorHashtags: crawler to capture tweets with precise geolocation (similar to TwitterMonitorGeolocation) according to the set of hashtags defined as parameter and independently of boundingbox.
* TwitterMonitorHashtagsNoCoords: crawler to collect samples with some geolocation defined (do not require precise GPS coords), but the samples match the set of hastags defined as parameter.

### Place Crawlers
* FoursquarePlaceCrawler
* InstagramPlaceCrawler

### Foursquare Place Classifier
* FoursquareCategories.json
* FoursquareCategories.py

### Spatiotemporal
* SpatiotemporalSimulator: simulator to estimate the encounter among users
* SpatiotemporalTraceExporter: exports the traces used in the SpatiotemporalSimulator.
