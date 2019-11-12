# A small scale QGIS plugin for an data preprocessing for a waterflow simulation project

This is a pocket-sized automation tool in form of a QGIS plugin for a friend's GIS project contract, which i know very little about. The sole purpose of this creation is to perform 3 basic tasks on 3 pre-existing layers:
- **F_RESZVIZGY**  a polygon layer storing Watershed locations and metadata.
- **P_CSAPADEKMERO** : a point layer storing rain gauge locations and metadata.
- **P_CSOMOPONT** : a point layer storing intersection point locations and metadata.

**Initial check:** First, the plugin asks for the user to select the layers which it must perform the tasks it was programmed to do. This is a very basic check which only seeks to validate the existence of certain metadata fields in the shape files selected.
After the initial check the function buttons get the enabled status. 

**Process A:** Iterating over the watershed polygon vertexes and checking if any of the intersection points overlap with the vertexes. If they do, it checks the HND and the various SUB_CATCH fields for a matching ID. If there is one, the polygon recieves the longest diagonal distance value as content for its S_LEFOLY field.

**Process B:** Calculating the nearest rain gauge location for the watershed polygons. Throughout nearest neighbor algorythm each of the polygons recieve the content of the NAME field of the rain gauge layer features as the "RAIN_GAUGE" field's value.

***NOTE:*** *This plugin was made over a few evenings, and the number one priority was to get it up and running as fast as possible. The structure reflects some bare-bone solutions and generic exception handling, the general lack of knowing even the most basic "why"-s regarding to the project itself, while often distregarding the principles of clean code and reusability. However I decided to upload this to showcase some of the "micro-projects" I am involved in.* 

The plugin's .ZIP installer can be downloaded also from this link:
https://mega.nz/#!Tk1XhKIL!V5IxEtybETaIMJpj2KYeZM6HB1xNuZhiJIX5yvVCdZE
