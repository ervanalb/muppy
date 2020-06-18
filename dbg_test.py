import logging
import muppy
import struct
import asyncio

logging.basicConfig(level=logging.INFO)

core = muppy.AsyncCore()
print(core.version)

rom = open("/home/eric/sm64.jp.z64", "rb").read()
core.rom_open(rom)

core.auto_attach_plugins()

n = 0
def p():
    global n
    print("Mario X:", struct.unpack("f", core.debug_mem_read_32(0x80339E3C))[0])
    print("Mario Y:", struct.unpack("f", core.debug_mem_read_32(0x80339E40))[0])
    print("Mario Z:", struct.unpack("f", core.debug_mem_read_32(0x80339E44))[0])
    speed = struct.unpack("f", core.debug_mem_read_32(0x80339E54))[0]
    print("Mario Speed:", speed)
    # Turn on at your own risk
    core.debug_mem_write_32(0x80339E54, struct.pack("f", speed * 1.1))
    n += 1

def start(pc: int):
    print("UPDATE: PC:", hex(pc))
    core.debug_set_run_state(muppy.DbgRunState.RUNNING)

#core.add_dbg_vi_callback(p)
#core.add_dbg_update_callback(start)

async def main():
    await core.a_execute()
    print("Running! Sleep for 10 second")
    await asyncio.sleep(3)
    await core.a_pause()
    await asyncio.sleep(1)
    await core.a_resume()
    await asyncio.sleep(3)
    await core.a_state_save("tmpfile")
    await asyncio.sleep(0.1)
    await core.a_state_load("tmpfile")
    print("Running! Sleep for 10 second")
    await asyncio.sleep(10)
    await core.a_stop()

asyncio.get_event_loop().run_until_complete(main())

core.detach_plugins()
core.rom_close()
