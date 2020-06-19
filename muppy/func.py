import logging
import struct
import threading
import time

from muppy import InputPlugin, ControllerInfo, Core, Plugin, PluginType, CoreParam, EmuState, DbgRunState, check_rc, Type
from typing import List, Optional, Any, Tuple

logger = logging.getLogger(__name__)

class FuncCore(Core):
    def __init__(self, rom: str, *args, graphics=False, **kwargs):
        super().__init__(*args, debugger=True, **kwargs)
        self.setup_core()
        self.connected_controllers = [True, False, False, False]
        rom = open(rom, "rb").read()
        self.rom_open(rom)
        p = FuncInputPlugin(self)
        if graphics:
            self.auto_attach_plugins(input_plugin=p)
        else:
            self.attach_plugin(p)
            vid_plugin = Plugin.make(self, self.default_video_plugin)
            if vid_plugin:
                self.attach_plugin(vid_plugin) # TODO remove this
            rsp_plugin = Plugin.make(self, self.default_rsp_plugin)
            if rsp_plugin:
                self.attach_plugin(rsp_plugin)
        self.add_dbg_update_callback(self.start)

        self.inputs = []
        self.mem_addrs = []
        self.mem = []

        self.thread = threading.Thread(target=self.execute, daemon=True)
        self.thread.start()
        while self.state_query(CoreParam.EMU_STATE) != EmuState.RUNNING:
            time.sleep(0.01)

    def setup_core(self):
        self.state_set(CoreParam.SPEED_LIMITER, 0)

        # XXX Turning off the OSD doesn't work?
        #section = self.ffi.new("m64p_handle *")
        #check_rc(self.handle.ConfigOpenSection(b"Core", section))
        #value = ffi.new("int *", 0)
        #self.handle.ConfigSetParameter(section, b"OnScreenDisplay", Type.BOOL, value)

        #section = self.ffi.new("m64p_handle *")
        #check_rc(self.handle.ConfigOpenSection(b"Video-Rice", section))
        #value = self.ffi.new("int *", 1)
        #self.handle.ConfigSetParameter(section, b"InN64Resolution", Type.BOOL, value)
        #value = self.ffi.new("int *", 1)
        #self.handle.ConfigSetParameter(section, b"ShowFPS", Type.BOOL, value)

    def start(self, _):
        self.debug_set_run_state(DbgRunState.RUNNING)

    def test(self, save_state=str, inputs=List[Tuple[int, int, int]], mem_addrs=List[Tuple[int, str]]):

        self.mem = []

        self.inputs = inputs
        self.mem_addrs = mem_addrs
        self.state_load(save_state)
        self.resume()
        while len(self.inputs) and self.thread.is_alive():
            time.sleep(0.01)
        if not self.thread.is_alive():
            raise RuntimeError("Mupen64plus process interrupted")
        return self.mem

    def read_memory(self):
        vec = []
        for addr, datatype in self.mem_addrs:
            size = struct.calcsize(datatype)
            assert size == 4 # TODO
            vec.append(*struct.unpack(datatype, self.debug_mem_read_32(addr)))
        self.mem.append(vec)

    def initiate_controllers(self):
        return [ControllerInfo(present=p, raw_data=False, plugin=False) for p in self.connected_controllers]

    def get_keys(self, controller: int) -> (int, int, int):
        no_input = (0, 0, 0)

        if not self.connected_controllers[controller]:
            return no_input

        self.read_memory()

        if len(self.inputs) == 0:
            self.pause()
            return no_input

        inputs = self.inputs.pop()

        return tuple(inputs)

    def close(self):
        self.stop()
        self.thread.join()
        self.detach_plugins()
        super().close()

class FuncInputPlugin(InputPlugin):
    def get_keys(self, controller: int) -> (int, int, int):
        return self.core.get_keys(controller)

    def initiate_controllers(self) -> List[ControllerInfo]:
        return self.core.initiate_controllers()
