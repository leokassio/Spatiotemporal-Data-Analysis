# Data Acquisition/Collection
Set of tools for data collection from Twitter, Foursquare and Instagram.

* TwitterMonitor.py: module to define the basic functions used by TwitterMonitor crawlers. Actually, it includes banner and configuration loaders.
* TwitterMonitor.cfg
* TwitterMonitor.cfg: the configuration file for Twitter crawlers. It defines the authentication dredentials, bounding boxes, hashtags among other parameters. It uses the Python SafeConfigParser to manage the configurations.
* TwitterMonitorGeolocation: crawler to capture the tweets with precise geolocation (samples with with GPS coords - latitude and longitude) determined by a bounding box, but independently of hashtags.
* TwitterMonitorHashtags: crawler to capture tweets with precise geolocation (similar to TwitterMonitorGeolocation) according to the set of hashtags defined as parameter and independently of boundingbox.
* TwitterMonitorHashtagsNoCoords: crawler to collect samples with some geolocation defined (do not require precise GPS coords), but the samples match the set of hastags defined as parameter.

### Place Crawlers
The place crawlers add contextual data for check-ins and geotagged photos. They obtain the place indicated by user and help to group the raw GPS coords.
* FoursquarePlaceCrawler: crawler to visit the check-in page and obtain the name and short url of place indicated by user.
* InstagramPlaceCrawler: crawler to visit the instagram photo URL and collect the users login, place name and URL.

### Foursquare Place Classifier
TBA
* FoursquareCategories.json
* FoursquareCategories.py: crawler to relate the Instagram places to Foursquare places. The main goal is capture the informations of places's categories.
* FoursquareCategories.py
