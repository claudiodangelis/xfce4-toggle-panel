#!/usr/bin/env python

#   Copyright 2013 Claudio "Dawson" d'Angelis <http://claudiodangelis.com/+>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from os import path
from xml.dom import minidom
import pickle
import re
import subprocess
import sys

p = subprocess.Popen(["xdotool","getmouselocation"], stdout=subprocess.PIPE)
output, error = p.communicate()
raw_current_coords=re.split("x|y|:| ", output)
CURRENT_X=raw_current_coords[2]
CURRENT_Y=raw_current_coords[5]

XFCE4_PANEL_CONFIG="~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml"
TMP_FILE="/tmp/xfce4-toggle-panel-rc"

autohide_panels = []
config_tree = minidom.parse(path.expanduser(XFCE4_PANEL_CONFIG))

for elem in config_tree.getElementsByTagName("property"):
    if (
        elem.getAttribute('name') == 'autohide' and
        elem.getAttribute('value') == "true"
        ):
        
        for subelem in elem.parentNode.getElementsByTagName("property"):
            if subelem.getAttribute("name") == "position":
                coords = subelem.getAttribute("value").split(";")
                autohide_panels.append(
                    [
                        str(re.split('=|\'',coords[1])[1]),
                        str(
                            int(str(re.split('=|\'',coords[2])[1])) +
                            int(str(re.split('=|\'',coords[0])[1])) + 1
                            )
                    ]
                )

if len(autohide_panels)==0:
    sys.exit()

def read_config():
    try:
        return pickle.load(open(TMP_FILE,"rb"))
    except Exception, e:
        return False

# Read configuration
config = {}

if read_config() is False:
    # Configuration file not found
    config["PANEL_INDEX"]=0
    config["CURRENT_X"]=CURRENT_X
    config["CURRENT_Y"]=CURRENT_Y
else:
    # Configuration file found
    config = read_config()

if [CURRENT_X,CURRENT_Y] not in autohide_panels:
    # Mouse cursor is not over a panel, starting from hovering the first panel
    config["CURRENT_X"]=CURRENT_X
    config["CURRENT_Y"]=CURRENT_Y
    subprocess.call(
        [
            "xdotool",
            "mousemove",
            autohide_panels[0][0], # First panel's X
            autohide_panels[0][1]  # First panel's Y
            ]
        )
    config["PANEL_INDEX"]=1

else:
    # Mouse cursor is hovering a panel, checking if there's a next panel to goto
    if config["PANEL_INDEX"] == (len(autohide_panels)):
        # Last panel, going back to original mouse cursor position
        config["PANEL_INDEX"]=0
        subprocess.call(
        [
            "xdotool",
            "mousemove",
            config["CURRENT_X"], # original position
            config["CURRENT_Y"]  # original position
            ]
        )

    else:
        # Going over the next panel
        panel_index=config["PANEL_INDEX"]
        subprocess.call(
        [
            "xdotool",
            "mousemove",
            autohide_panels[panel_index][0], # panel's X
            autohide_panels[panel_index][1]  # panel's Y
            ]
        )
        config["PANEL_INDEX"]+=1

pickle.dump(config,open(TMP_FILE,"wb"))