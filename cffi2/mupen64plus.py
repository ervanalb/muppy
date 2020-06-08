from cffi import FFI
from enum import Enum, Flag
from collections import namedtuple
from typing import Optional
import ctypes, ctypes.util

CORE_API_VERSION = 0x20001

ffi = FFI()

with open("cdefs.h") as f:
    ffi.cdef(f.read())

# Note: this might not work on Windows, but dlopen on any library will do.
C = ffi.dlopen(ctypes.util.find_library('c'))

class Mupen64PlusError(Exception):
    pass

def gen_enum(base, name: str, prefix: str):
    syms = filter(lambda x: x.startswith(prefix), dir(C))
    return base(name, {sym[len(prefix):]: getattr(C, sym) for sym in syms})

def check_rc(rc):
    if rc == C.M64ERR_SUCCESS:
        return

    raise {
        C.M64ERR_NOT_INIT: Mupen64PlusError("Not initialized"),
        C.M64ERR_ALREADY_INIT: Mupen64PlusError("Already initialized"),
        C.M64ERR_INCOMPATIBLE: Mupen64PlusError("Incompatible version"),
        C.M64ERR_INPUT_ASSERT: Mupen64PlusError("Input assert"),
        C.M64ERR_INPUT_INVALID: Mupen64PlusError("Input invalid"),
        C.M64ERR_INPUT_NOT_FOUND: Mupen64PlusError("Input not found"),
        C.M64ERR_NO_MEMORY: MemoryError(),
        C.M64ERR_FILES: Mupen64PlusError("Files"),
        C.M64ERR_INTERNAL: Mupen64PlusError("Internal error"),
        C.M64ERR_INVALID_STATE: Mupen64PlusError("Invalid state"),
        C.M64ERR_PLUGIN_FAIL: Mupen64PlusError("Plugin failed"),
        C.M64ERR_SYSTEM_FAIL: Mupen64PlusError("System failed"),
        C.M64ERR_UNSUPPORTED: Mupen64PlusError("Unsupported"),
        C.M64ERR_WRONG_TYPE: Mupen64PlusError("Wrong type"),
    }.get(rc, Mupen64PlusError("Unknown return code"))

## Enums

PluginType = gen_enum(Enum, "PluginType", "M64PLUGIN_")
CoreCaps = gen_enum(Flag, "CoreCaps", "M64CAPS_")
CoreParam = gen_enum(Enum, "CoreParam", "M64CORE_")
MsgLevel = gen_enum(Enum, "MsgLevel", "M64MSG_")

# Named tuples (for return values)

Version = namedtuple("Version", ("plugin_type", "plugin_version", "api_version", "plugin_name", "capabilities"))

# Functions

class DynamicLibrary:
    def __init__(self, dl=None):
        self.handle = None
        self.dl = self.DL if dl is None else dl
        self.handle_raw = ffi.cast("void *", ctypes.CDLL(self.dl)._handle)
        self.handle = ffi.dlopen(self.handle_raw)

    def __del__(self):
        self.close()

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

class Core(DynamicLibrary):
    DL = "libmupen64plus.so"

    def __init__(self, config_path: Optional[str]=None, data_path: Optional[str]=None, dl: Optional[str]=None):
        self.open = False
        super().__init__(dl=dl)

        config_path = ffi.NULL if config_path is None else ffi.new("char[]", bytes(config_path, encoding="utf8"))
        data_path = ffi.NULL if data_path is None else ffi.new("char[]", bytes(data_path, encoding="utf8"))

        @ffi.callback("ptr_StateCallback")
        def _state_callback(_, param_type, new_value):
            self.state_callback(CoreParam(param_type), new_value)

        @ffi.callback("ptr_DebugCallback")
        def _debug_callback(_, level, message):
            self.debug_callback(MsgLevel(level), str(ffi.string(message), encoding="utf8"))

        check_rc(self.handle.CoreStartup(
            CORE_API_VERSION,
            config_path,
            data_path,
            ffi.NULL,
            _debug_callback,
            ffi.NULL,
            _state_callback,
        ))

        self.open = True

    def close(self):
        if self.open:
            check_rc(self.handle.CoreShutdown())
            self.open = False
        super().close()

    def state_callback(self, param_type, new_value):
        pass

    def debug_callback(self, level, message):
        print(level, message)

class Plugin(DynamicLibrary):
    def __init__(self, core: Core, dl: Optional[str]=None):
        self.open = False
        super().__init__(dl=dl)
        self.core = core

        @ffi.callback("ptr_DebugCallback")
        def _debug_callback(_, level, message):
            self.core.debug_callback(MsgLevel(level), str(ffi.string(message), encoding="utf8"))

        check_rc(self.handle.PluginStartup(
            self.core.handle_raw,
            ffi.NULL,
            _debug_callback,
        ))

        self.open = True

    def close(self):
        if self.open:
            check_rc(self.handle.PluginShutdown())
            self.open = False
        super().close()
