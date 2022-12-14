# punch-out-wii-noesis-plugin
A noesis plugin to extract Punch-Out!! Wii models with their meshes and rig.

Huge thanks to the kind and wonderful people at the XeNTaX server who helped make this possible by identifying a lot of sections that I could not see before and assisting with sections of the code. Their help has been invaluable, and this wouldn't have been possible without them!

Addittionally, thanks to the creators at Switch Toolbox who made the code there that a lot of this plugin is based on. Without their code, I wouldn't know what I'm looking at!

Limitations:
- You'll need to obtain the models textures yourself by other means.
- The coordinates in Punch-Out!! are (x, -z, y) but I did not adjust for this, so the models will reflect that.
- The model meshes and joints are not given their native names. There is likely a way to make that possible, but I'm not going to implement it since I don't think it is entirely necessary.
- Weights seem odd sometimes. Reccomend some self-adjustment when using them for personal use. Working to see if this is just normal because the game seems to animate itself to work around these limits in weights.
- Crowd models export with a skeleton, but no weights or bone parenting.

# How to use:
1. [Get the Noesis program here.](https://richwhitehouse.com/index.php?content=inc_projects.php)
2. Download the fmt_powiidict.py file from this repository.
3. Extract the .zip file the program comes in. 
4. Go to ../noesisv4466/plugins/python
5. Move the fmt_powiidict.py to the python folder.
6. Open Noesis and start exploring!
