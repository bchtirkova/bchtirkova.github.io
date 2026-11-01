# NOTE B: There is frontmatter and python-frontmatter that are different packages. You need the second one. Run through argo-venv
# Edits _talks/talkmap; run from base

# Leaflet cluster map of talk locations
#
# The _talks/ directory contains .md files of all your
# talks. This scrapes the location YAML field from each .md file, geolocates it
# with geopy/Nominatim, and uses the getorg library to output data, HTML, and
# Javascript for a standalone cluster map. This is functionally the same as the
# talkmap Jupyter notebook.
import time
import frontmatter
import glob
import getorg
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut
from pathlib import Path

# Set the default timeout, in seconds
TIMEOUT = 15

# Collect the Markdown files
g = glob.glob("_talks/*.md")

# Prepare to geolocate
geocoder = Nominatim(user_agent="academicpages.github.io")
location_dict = {}
location = ""
permalink = ""
title = ""

# Perform geolocation
for file in g:
    # Read the file
    data = frontmatter.load(file)
    data = data.to_dict()

    # Press on if the location is not present
    if 'location' not in data:
        continue

    # Prepare the description
    title = data['title'].strip()
    # B: I'm not filling in the venue part of the json. If ever included, edit here.
    # venue = data['venue'].strip()
    venue = ""
    location = data['location'].strip()
    description = f"{title}<br />{venue}; {location}"

    # Geocode the location and report the status
    try:
        time.sleep(10)  # sleep 10 seconds to not get 429 too many requests
        location_dict[description] = geocoder.geocode(location, timeout=TIMEOUT)
        print(description, location_dict[description])
    except ValueError as ex:
        print(f"Error: geocode failed on input {location} with message {ex}")
    except GeocoderTimedOut as ex:
        print(f"Error: geocode timed out on input {location} with message {ex}")
    except Exception as ex:
        print(f"An unhandled exception occurred while processing input {location} with message {ex}")

# Save the map
m = getorg.orgmap.create_map_obj()
getorg.orgmap.output_html_cluster_map(location_dict, folder_name="_talks/talkmap", hashed_usernames=False)


# B: Overwrite getorg's map.html to use overpass.ch vector tiles (MapLibre style)
# instead of the hard-coded Esri tiles. The markers still come from org-locations.js.
OVERPASS_KEY = "ovp_OeUOgK1oOvpvA2ANf2oRDAzbPGtUlFi6"
STYLE_URL = f"https://api.overpass.ch/v1/{OVERPASS_KEY}/maps/styles/marine.json?lang=en&hillshade=1"

map_path = Path("_talks/talkmap") / "map.html"

html = f"""<!DOCTYPE html>
<html>
<head>
	<title>Talk map</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">

	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css" />
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/maplibre-gl@5.24.0/dist/maplibre-gl.css" />
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
	<style>
		html, body, #map {{ margin: 0; width: 100%; height: 100%; }}
	</style>

	<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
	<script src="https://cdn.jsdelivr.net/npm/maplibre-gl@5.24.0/dist/maplibre-gl.js"></script>
	<script src="https://cdn.jsdelivr.net/npm/@maplibre/maplibre-gl-leaflet@0.1.4/leaflet-maplibre-gl.js"></script>
	<script src="https://cdn.jsdelivr.net/npm/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
	<script src="org-locations.js"></script>
</head>
<body>
	<div id="map"></div>
	<script type="text/javascript">
		var map = L.map('map', {{maxZoom: 18}});
		L.maplibreGL({{
			style: '{STYLE_URL}'
		}}).addTo(map);

		var markers = L.markerClusterGroup({{
			showCoverageOnHover: false,
			maxClusterRadius: 15
		}});
		for (var i = 0; i < addressPoints.length; i++) {{
			var a = addressPoints[i];
			var marker = L.marker(L.latLng(a[1], a[2]), {{ title: a[0] }});
			marker.bindPopup(a[0]);
			markers.addLayer(marker);
		}}
		map.addLayer(markers);
		// Fit all talks (Hawaii to China) in the view
		map.fitBounds(markers.getBounds(), {{padding: [30, 30]}});
	</script>
</body>
</html>
"""
map_path.write_text(html, encoding="utf-8")
