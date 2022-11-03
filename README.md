# punch-out-wii-noesis-plugin
A noesis plugin to extract Punch-Out!! Wii models with their meshes and rig.

Huge thanks to the kind and wonderful people at the XeNTaX server who helped make this possible by identifying a lot of sections that I could not see before and assisting with sections of the code. Their help has been invaluable, and this wouldn't have been possible without them!

Limitations:
- You'll need to obtain the models textures yourself by other means.
- I also do not have the UV maps decoded yet either, so you'll have to set those yourself as well.
- The coordinates in Punch-Out!! are (x, -z, y) but I did not adjust for this, so the models will reflect that.
- The model meshes and joints are not given their native names. There is likely a way to make that possible, but I'm not going to implement it since I don't think it is entirely necessary.
- Weights are currently buggy. Reccomend some self-adjustment when using them. Working to see if these can be fixed.
- Crowd models export with a skeleton, but no weights or bone parenting.
- Also I forgot to take out the debug window so if it annoys you, open the .py file in something like notepad and remove this code (lines 16-18):
`    noesis.logPopup()`

  `print(`

  `"The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")`

# How to use:
1. [Get the Noesis program here.](https://richwhitehouse.com/index.php?content=inc_projects.php)
2. Download the fmt_powiidict.py file from this repository.
3. Extract the .zip file the program comes in. 
4. Go to ../noesisv4466/plugins/python
5. Move the fmt_powiidict.py to the python folder.
6. Open Noesis and start exploring!
