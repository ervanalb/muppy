import logging
import muppy
from muppy.tas import TASPlayer

logging.basicConfig(level=logging.INFO)

core = muppy.Core()
print(core.version)

rom = open("/home/eric/sm64.jp.z64", "rb").read()
core.rom_open(rom)

p = muppy.tas.TASPlayer(core, "sm64tas.m64", backup_plugin=core.default_input_plugin)
core.auto_attach_plugins(input_plugin=p)
core.execute()

# User can quit with Esc

core.detach_plugins()
core.rom_close()
