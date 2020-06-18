import logging
import muppy

logging.basicConfig(level=logging.INFO)

core = muppy.Core(debugger=True)
print(core.version)

rom = open("/home/eric/sm64.jp.z64", "rb").read()
core.rom_open(rom)

core.auto_attach_plugins()

n = 0
def p():
    global n
    print("Frame!", n)
    n += 1

def start(pc: int):
    print("UPDATE: PC:", hex(pc))
    core.debug_set_run_state(muppy.DbgRunState.RUNNING)

core.add_dbg_vi_callback(p)
core.add_dbg_update_callback(start)
core.execute()

# User can quit with Esc

core.detach_plugins()
core.rom_close()
