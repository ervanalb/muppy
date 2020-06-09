import logging
import mupen64plus

logging.basicConfig(level=logging.INFO)

core = mupen64plus.Core()
print(core.version)

rom = open("/home/eric/sm64/baserom.jp.z64", "rb").read()
core.rom_open(rom)

core.auto_attach_plugins()

core.execute()

# User can quit with Esc

core.detach_plugins()
core.rom_close()
