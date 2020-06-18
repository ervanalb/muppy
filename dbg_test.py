import logging
import muppy
import struct

logging.basicConfig(level=logging.INFO)

core = muppy.Core(debugger=True)
print(core.version)

rom = open("/home/eric/sm64.jp.z64", "rb").read()
core.rom_open(rom)

core.auto_attach_plugins()

n = 0
ss = None

def p():
    global n, ss
    print("Frame", n)
    #print("Mario X:", struct.unpack("f", core.debug_mem_read_32(0x80339E3C))[0])
    #print("Mario Y:", struct.unpack("f", core.debug_mem_read_32(0x80339E40))[0])
    #print("Mario Z:", struct.unpack("f", core.debug_mem_read_32(0x80339E44))[0])
    speed = struct.unpack("f", core.debug_mem_read_32(0x80339E54))[0]
    #print("Mario Speed:", speed)
    # Turn on at your own risk
    core.debug_mem_write_32(0x80339E54, struct.pack("f", speed * 1.1))
    n += 1

    if n == 1000:
        ss = core.state_save_data()
        print(ss)
    elif n > 1000 and n % 300 == 0:
        core.state_load_data(ss)

def start(pc: int):
    print("UPDATE: PC:", hex(pc))
    core.debug_set_run_state(muppy.DbgRunState.RUNNING)

core.add_dbg_vi_callback(p)
core.add_dbg_update_callback(start)
core.execute()

# User can quit with Esc

core.detach_plugins()
core.rom_close()
