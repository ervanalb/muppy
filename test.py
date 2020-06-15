import logging
import muppy

logging.basicConfig(level=logging.INFO)

core = muppy.Core()
print(core.version)

rom = open("/home/eric/sm64.jp.z64", "rb").read()
core.rom_open(rom)

p = muppy.InputPlugin(core)

core.auto_attach_plugins(input_plugin=muppy.InputPlugin)

core.execute()

# User can quit with Esc

core.detach_plugins()
core.rom_close()
