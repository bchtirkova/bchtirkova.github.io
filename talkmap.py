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


# Manually remove this text from map.html because someone hard-coded it in getorg.
map_path = Path("_talks/talkmap") / "map.html"

text_to_remove = (
    "Mouse over a cluster to see the bounds of its children "
    "and click a cluster to zoom to those bounds"
)

html = map_path.read_text(encoding="utf-8")
html = html.replace(text_to_remove, "")
map_path.write_text(html, encoding="utf-8")
