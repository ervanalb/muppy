from cffi import FFI
from enum import IntEnum, IntFlag
from collections import namedtuple
from typing import Optional, List, Any
import ctypes, ctypes.util
import logging
import os
import pkg_resources
import inspect
import functools

CORE_API_VERSION = 0x20001

ffi = FFI()

ffi.cdef(str(pkg_resources.resource_string(__name__, "cdefs.h"), encoding="utf8"))
ffi.cdef("void *handle;") # for Python plugins

# Note: this might not work on Windows, but dlopen on any library will do.
C = ffi.dlopen(ctypes.util.find_library('c'))

class Mupen64PlusError(Exception):
    pass

def gen_enum(base, name: str, prefix: str):
    syms = filter(lambda x: x.startswith(prefix), dir(C))
    return base(name, {sym[len(prefix):]: getattr(C, sym) for sym in syms})

## Enums

Error = gen_enum(IntEnum, "Error", "M64ERR_")
PluginType = gen_enum(IntEnum, "PluginType", "M64PLUGIN_")
CoreCaps = gen_enum(IntFlag, "CoreCaps", "M64CAPS_")
CoreParam = gen_enum(IntEnum, "CoreParam", "M64CORE_")
MsgLevel = gen_enum(IntEnum, "MsgLevel", "M64MSG_")
Command = gen_enum(IntEnum, "Command", "M64CMD_")
Type = gen_enum(IntEnum, "Type", "M64TYPE_")
EmuState = gen_enum(IntEnum, "EmuState", "M64EMU_")
DbgRunState = gen_enum(IntEnum, "DbgRunState", "M64P_DBG_RUNSTATE_")

LOGLEVEL = {
    MsgLevel.ERROR: logging.ERROR,
    MsgLevel.WARNING: logging.WARNING,
    MsgLevel.INFO: logging.INFO,
    MsgLevel.STATUS: logging.INFO,
    MsgLevel.VERBOSE: logging.DEBUG,
}

logger = logging.getLogger(__name__)

# Named tuples (for return values)

Version = namedtuple("Version", ("plugin_type", "plugin_version", "api_version", "plugin_name", "capabilities"))

ControllerInfo = namedtuple("ControllerInfo", ("present", "raw_data", "plugin"))

# Util

def check_rc(rc):
    if rc == Error.SUCCESS:
        return

    raise {
        Error.NOT_INIT: Mupen64PlusError("Not initialized"),
        Error.ALREADY_INIT: Mupen64PlusError("Already initialized"),
        Error.INCOMPATIBLE: Mupen64PlusError("Incompatible version"),
        Error.INPUT_ASSERT: Mupen64PlusError("Input assert"),
        Error.INPUT_INVALID: Mupen64PlusError("Input invalid"),
        Error.INPUT_NOT_FOUND: Mupen64PlusError("Input not found"),
        Error.NO_MEMORY: MemoryError(),
        Error.FILES: Mupen64PlusError("Files"),
        Error.INTERNAL: Mupen64PlusError("Internal error"),
        Error.INVALID_STATE: Mupen64PlusError("Invalid state"),
        Error.PLUGIN_FAIL: Mupen64PlusError("Plugin failed"),
        Error.SYSTEM_FAIL: Mupen64PlusError("System failed"),
        Error.UNSUPPORTED: Mupen64PlusError("Unsupported"),
        Error.WRONG_TYPE: Mupen64PlusError("Wrong type"),
    }.get(rc, Mupen64PlusError("Unknown return code"))

def requires_debugger(f):
    @functools.wraps(f)
    def _wrapper(self, *args, **kwargs):
        if not self.version.capabilities & CoreCaps.DEBUGGER:
            raise Mupen64PlusError("Core does not have debugger capability")
        if not self.debugger:
            raise Mupen64PlusError("Debugger not enabled")
        return f(self, *args, **kwargs)
    return _wrapper

# Functions

class DynamicLibrary:
    def __init__(self, dl=None):
        self.handle = None
        self.dl = self.DL if dl is None else dl
        self.handle_raw = ffi.cast("void *", ctypes.CDLL(self.dl)._handle)
        self.handle = ffi.dlopen(self.handle_raw)
        self.ptr = ffi.new_handle(self)

    def __del__(self):
        pass
        #self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.handle:
            ffi.dlclose(self.handle)
            self.handle = None

    def plugin_get_version(self):
        plugin_type = ffi.new("m64p_plugin_type *")
        plugin_version = ffi.new("int *")
        api_version = ffi.new("int *")
        plugin_name = ffi.new("const char **")
        capabilities = ffi.new("int *")
    
        check_rc(self.handle.PluginGetVersion(plugin_type, plugin_version, api_version, plugin_name, capabilities))
        return Version(PluginType(plugin_type[0]), plugin_version[0], api_version[0], str(ffi.string(plugin_name[0]), encoding="utf8"), CoreCaps(capabilities[0]))

@ffi.callback("ptr_StateCallback")
def _state_callback(ctx, param_type, new_value):
    ffi.from_handle(ctx).state_callback(CoreParam(param_type), new_value)

@ffi.callback("ptr_DebugCallback")
def _debug_callback(ctx, level, message):
    ffi.from_handle(ctx).debug_callback(MsgLevel(level), str(ffi.string(message), encoding="utf8"))

class Core(DynamicLibrary):
    DL = "libmupen64plus.so"

    def __init__(self, config_path: Optional[str]=None, data_path: Optional[str]=None, dl: Optional[str]=None, debugger=False):
        self.open = False
        super().__init__(dl=dl)

        config_path = ffi.NULL if config_path is None else ffi.new("char[]", bytes(config_path, encoding="utf8"))
        data_path = ffi.NULL if data_path is None else ffi.new("char[]", bytes(data_path, encoding="utf8"))

        check_rc(self.handle.CoreStartup(
            CORE_API_VERSION,
            config_path,
            data_path,
            self.ptr,
            _debug_callback,
            self.ptr,
            _state_callback,
        ))

        self.plugins = []
        self.open = True
        self.version = self.plugin_get_version()
        self.get_default_plugins()

        self.video_plugin = None
        self.audio_plugin = None
        self.input_plugin = None
        self.rsp_plugin = None

        self.state_callbacks = []

        self.debugger = debugger
        if debugger:
            self.init_debugger()
        self.config_debugger(debugger)

    def config_debugger(self, value):
        section = ffi.new("m64p_handle *")
        check_rc(self.handle.ConfigOpenSection(b"Core", section))
        value = ffi.new("int *", self.debugger)
        self.handle.ConfigSetParameter(section, b"EnableDebugger", Type.BOOL, value)

    @requires_debugger
    def init_debugger(self):
        @ffi.callback("void ()")
        def _dbg_frontend_init():
            self.dbg_init_callback()
        self._dbg_frontend_init = _dbg_frontend_init

        @ffi.callback("void (unsigned int)")
        def _dbg_frontend_update(pc):
            self.dbg_update_callback(pc)
        self._dbg_frontend_update = _dbg_frontend_update

        @ffi.callback("void ()")
        def _dbg_frontend_vi():
            self.dbg_vi_callback()
        self._dbg_frontend_vi = _dbg_frontend_vi

        check_rc(self.handle.DebugSetCallbacks(_dbg_frontend_init, _dbg_frontend_update, _dbg_frontend_vi))

        self.dbg_vi_callbacks = []
        self.dbg_update_callbacks = []

    def close(self):
        if self.open:
            check_rc(self.handle.CoreShutdown())
            self.open = False
        super().close()

    def add_state_callback(self, callback):
        self.state_callbacks.append(callback)

    def remove_state_callback(self, callback):
        self.state_callbacks.remove(callback)

    def state_callback(self, param_type, new_value):
        for cb in self.state_callbacks:
            cb(param_type, new_value)

    def dbg_init_callback(self):
        logger.info("Debugger initialized")

    def dbg_vi_callback(self):
        for cb in self.dbg_vi_callbacks:
            cb()

    def dbg_update_callback(self, pc: int):
        for cb in self.dbg_update_callbacks:
            cb(pc)

    def debug_callback(self, level, message):
        loglvl = LOGLEVEL.get(level, logging.NOTSET)
        logger.log(loglvl, message)

    def rom_open(self, rom: bytes):
        check_rc(self.handle.CoreDoCommand(Command.ROM_OPEN, len(rom), rom))

    def rom_close(self):
        check_rc(self.handle.CoreDoCommand(Command.ROM_CLOSE, 0, ffi.NULL))

    def attach_plugin(self, plugin: "Plugin"):
        for plugin_type in ["video", "audio", "input", "rsp"]:
            if plugin.version.plugin_type == getattr(PluginType, plugin_type.upper().replace("VIDEO", "GFX")):
                existing_plugin = getattr(self, plugin_type.lower() + "_plugin")
                if existing_plugin is not None:
                    self.detach_plugin(existing_plugin)
                check_rc(self.handle.CoreAttachPlugin(plugin.version.plugin_type, plugin.handle_raw))
                setattr(self, plugin_type.lower() + "_plugin", plugin)
                break
        else:
            raise ValueError("Unknown plugin type")

    def detach_plugin(self, plugin: "Plugin"):
        for plugin_type in ["video", "audio", "input", "rsp"]:
            existing_plugin = getattr(self, plugin_type.lower() + "_plugin")
            if existing_plugin == plugin:
                check_rc(self.handle.CoreDetachPlugin(plugin.version.plugin_type))
                setattr(self, plugin_type.lower() + "_plugin", None)
                break
        else: # on for loop
            raise ValueError("Plugin not attached")

    def detach_plugins(self):
        for plugin_type in ["rsp", "input", "audio", "video"]:
            existing_plugin = getattr(self, plugin_type.lower() + "_plugin")
            if existing_plugin is not None:
                self.detach_plugin(existing_plugin)

    def get_default_plugins(self):
        section = ffi.new("m64p_handle *")
        check_rc(self.handle.ConfigOpenSection(b"UI-Console", section))
        static_string = ffi.new("char[1024]")

        rc = self.handle.ConfigGetParameter(section[0], b"PluginDir", Type.STRING, static_string, 1024)
        if rc == Error.SUCCESS:
            self.plugin_dir = str(ffi.string(static_string), encoding="utf8")
        elif rc == Error.INPUT_INVALID:
            self.plugin_dir = ""
        else:
            check_rc(rc)

        def get_plugin(plugin_name):
            rc = self.handle.ConfigGetParameter(section[0], bytes(plugin_name, encoding="latin1"), Type.STRING, static_string, 1024)
            if rc == Error.SUCCESS:
                return os.path.abspath(os.path.join(self.plugin_dir, str(ffi.string(static_string), encoding="utf8")))
            elif rc == Error.INPUT_INVALID:
                return None
            else:
                check_rc(rc)
            assert False

        self.default_video_plugin = get_plugin("VideoPlugin")
        self.default_audio_plugin = get_plugin("AudioPlugin")
        self.default_input_plugin = get_plugin("InputPlugin")
        self.default_rsp_plugin = get_plugin("RspPlugin")

    def auto_attach_plugins(self, video_plugin=None, audio_plugin=None, input_plugin=None, rsp_plugin=None):
        video_plugin = Plugin.make(self, video_plugin or self.default_video_plugin)
        audio_plugin = Plugin.make(self, audio_plugin or self.default_audio_plugin)
        input_plugin = Plugin.make(self, input_plugin or self.default_input_plugin)
        rsp_plugin   = Plugin.make(self, rsp_plugin or self.default_rsp_plugin)

        if self.video_plugin is None:
            logger.warn("No video plugin")
        if self.audio_plugin is None:
            logger.warn("No audio plugin")
        if self.input_plugin is None:
            logger.warn("No input plugin")
        if self.rsp_plugin is None:
            logger.warn("No RSP plugin")

        plugins = [p for p in [
            video_plugin,
            audio_plugin,
            input_plugin,
            rsp_plugin,
        ] if p is not None]

        for plugin in plugins:
            self.attach_plugin(plugin)

    def execute(self):
        check_rc(self.handle.CoreDoCommand(Command.EXECUTE, 0, ffi.NULL))

    def stop(self):
        check_rc(self.handle.CoreDoCommand(Command.STOP, 0, ffi.NULL))

    def pause(self):
        check_rc(self.handle.CoreDoCommand(Command.PAUSE, 0, ffi.NULL))

    def resume(self):
        check_rc(self.handle.CoreDoCommand(Command.RESUME, 0, ffi.NULL))

    def state_save(self, filename=None):
        check_rc(self.handle.CoreDoCommand(Command.STATE_SAVE, 1, bytes(filename, encoding="utf8")))

    def state_load(self, filename=None):
        check_rc(self.handle.CoreDoCommand(Command.STATE_LOAD, 1, bytes(filename, encoding="utf8")))

    def state_query(self, param: CoreParam) -> int:
        value = ffi.new("int *")
        check_rc(self.handle.CoreDoCommand(Command.STATE_QUERY, param, value))
        return value[0]

    def state_set(self, param: CoreParam, value: int) -> None:
        value_ptr = ffi.new("int *", value)
        check_rc(self.handle.CoreDoCommand(Command.STATE_QUERY, param, value_ptr))

    def debug_mem_read_64(self, address: int) -> int:
        return struct.pack("=L", self.handle.DebugMemRead64(address))

    def debug_mem_read_32(self, address: int) -> int:
        return struct.pack("=I", self.handle.DebugMemRead32(address))

    def debug_mem_read_16(self, address: int) -> int:
        return struct.pack("=H", self.handle.DebugMemRead16(address))

    def debug_mem_read_8(self, address: int) -> int:
        return struct.pack("=B", self.handle.DebugMemRead16(address))

    def debug_mem_write_64(self, address: int, value: bytes) -> None:
        return self.handle.DebugMemRead64(address, struct.unpack("=L", value)[0])

    @requires_debugger
    def debug_set_run_state(self, runstate: DbgRunState) -> None:
        check_rc(self.handle.DebugSetRunState(runstate))

    @requires_debugger
    def add_dbg_vi_callback(self, callback):
        self.dbg_vi_callbacks.append(callback)

    @requires_debugger
    def remove_dbg_vi_callback(self, callback):
        self.dbg_vi_callbacks.remove(callback)

    @requires_debugger
    def add_dbg_update_callback(self, callback):
        self.dbg_update_callbacks.append(callback)

    @requires_debugger
    def remove_dbg_update_callback(self, callback):
        self.dbg_update_callbacks.remove(callback)

class Plugin(DynamicLibrary):
    def __init__(self, core: Core, dl: Optional[str]=None):
        self.open = False
        super().__init__(dl=dl)
        self.core = core

        check_rc(self.handle.PluginStartup(
            self.core.handle_raw,
            self.core.ptr,
            _debug_callback,
        ))

        self.open = True
        self.version = self.plugin_get_version()

    def close(self):
        if self.open:
            check_rc(self.handle.PluginShutdown())
            self.open = False
        super().close()

    @classmethod
    def make(self, core: Core, plugin: Any):
        if plugin is None:
            return None
        elif isinstance(plugin, str):
            plugin_path = os.path.abspath(os.path.join(core.plugin_dir, plugin))
            return Plugin(core, dl=plugin_path)
        elif inspect.isclass(plugin):
            return plugin(core)
        else:
            return plugin

class PythonPlugin(Plugin):
    # Override me!
    plugin_name = "Custom Python Plugin"
    plugin_version = 0x000001

    def __init__(self, core: Core, dl: Optional[str]=None):
        self.open = False
        DynamicLibrary.__init__(self)
        self.core = core
        self.handle.handle = ffi.cast("void *", id(self)) # XXX using id to get a pointer seems sketchy

        check_rc(self.handle.PluginStartup(
            self.core.handle_raw,
            self.core.ptr,
            _debug_callback,
        ))

        self.open = True
        self.version = self.plugin_get_version()
        self.plugin_startup()

    def close(self):
        if self.open:
            self.plugin_shutdown()
            check_rc(self.handle.PluginShutdown())
            self.open = False
        super().close()

    # Override me!
    def plugin_startup(self):
        pass

    # Override me!
    def plugin_shutdown(self):
        pass

class InputPlugin(PythonPlugin):
    DL = pkg_resources.resource_filename(__name__, "mupen64plus-input-python.so")
    plugin_name = "Custom Python Input Plugin"

    def get_keys(self, controller: int) -> (int, int, int):
        return (0, 0, 0)

    def initiate_controllers(self) -> List[ControllerInfo]:
        return [ControllerInfo(present=False, raw_data=False, plugin=False)] * 4
