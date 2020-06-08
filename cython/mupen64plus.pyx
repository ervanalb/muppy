cimport cmupen64plus as c
cimport dlopen, dlclose, RTLD_LAZY, dlsym from dlfcn
from enum import Enum, Flag
from collections import namedtuple
from typing import Optional

CORE_API_VERSION = 0x20001

class Mupen64PlusError(Exception):
    pass

class DynamicLibraryError(Exception):
    pass

def check_rc(rc):
    if rc == c.M64ERR_SUCCESS:
        return

    raise {
        c.M64ERR_NOT_INIT: Mupen64PlusError("Not initialized"),
        c.M64ERR_ALREADY_INIT: Mupen64PlusError("Already initialized"),
        c.M64ERR_INCOMPATIBLE: Mupen64PlusError("Incompatible version"),
        c.M64ERR_INPUT_ASSERT: Mupen64PlusError("Input assert"),
        c.M64ERR_INPUT_INVALID: Mupen64PlusError("Input invalid"),
        c.M64ERR_INPUT_NOT_FOUND: Mupen64PlusError("Input not found"),
        c.M64ERR_NO_MEMORY: MemoryError(),
        c.M64ERR_FILES: Mupen64PlusError("Files"),
        c.M64ERR_INTERNAL: Mupen64PlusError("Internal error"),
        c.M64ERR_INVALID_STATE: Mupen64PlusError("Invalid state"),
        c.M64ERR_PLUGIN_FAIL: Mupen64PlusError("Plugin failed"),
        c.M64ERR_SYSTEM_FAIL: Mupen64PlusError("System failed"),
        c.M64ERR_UNSUPPORTED: Mupen64PlusError("Unsupported"),
        c.M64ERR_WRONG_TYPE: Mupen64PlusError("Wrong type"),
    }.get(rc, Mupen64PlusError("Unknown return code"))

# Enums

PluginType = Enum("PluginType", {
    "NULL": c.M64PLUGIN_NULL,
    "RSP": c.M64PLUGIN_RSP,
    "GFX": c.M64PLUGIN_GFX,
    "AUDIO": c.M64PLUGIN_AUDIO,
    "INPUT": c.M64PLUGIN_INPUT,
    "CORE": c.M64PLUGIN_CORE
})

CoreCaps = Flag("CoreCaps", {
    "DYNAREC": 1,
    "DEBUGGER": 2,
    "CORE_COMPARE": 4,
})

# Named tuples (for return values)

Version = namedtuple("Version", ("plugin_type", "plugin_version", "api_version", "plugin_name", "capabilities"))

# Functions

def plugin_get_version():
    cdef c.m64p_plugin_type plugin_type
    cdef int plugin_version
    cdef int api_version
    cdef const char *plugin_name
    cdef int capabilities

    check_rc(c.PluginGetVersion(&plugin_type, &plugin_version, &api_version, &plugin_name, &capabilities))
    return Version(PluginType(plugin_type), plugin_version, api_version, str(plugin_name, encoding="utf8"), CoreCaps(capabilities))


#    ctypedef void (*ptr_StateCallback)(void *Context, m64p_core_param param_type, int new_value)
#    ctypedef void (*ptr_DebugCallback)(void *Context, int level, const char *message)
cdef void _state_callback(void *context, c.m64p_core_param param_type, int new_value):
    (<object>context).state_callback(param_type, new_value)

cdef void _debug_callback(void *context, int level, const char *message):
    (<object>context).state_callback(level, message)

def dl_check(success):
    if success:
        return success
    raise DynamicLibraryError(str(dlerror(), encoding="utf8"))

class Plugin:
    def __init__(self, path: str):
        self.handle = NULL
        self.handle = dl_check(dlopen(bytes(path, encoding="utf8"), RTLD_LAZY))

        setup_pointers()
        check_rc(self.plugin_startup())
        self.open = True

    def setup_pointers(self):
        self.plugin_startup_ptr = dl_check(dlsym(self.handle, b"PluginStartup"))
        self.plugin_shutdown_ptr = dl_check(dlsym(self.handle, b"PluginShutdown"))
        self.plugin_get_version_ptr = dl_check(dlsym(self.handle, b"PluginGetVersion"))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.handle:
            dl_check(self.dlclose(self.handle) == 0)
            self.handle = NULL

    def __dealloc__(self):
        self.close()

    def plugin_startup(self, core: Core, 


class Core:
    def __init__(self, config_path: Optional[str]=None, data_path: Optional[str]=None):
        if config_path is not None:
            config_path_bytes = bytes(config_path, encoding="utf8")
        if data_path is not None:
            data_path_bytes = bytes(data_path, encoding="utf8")
        check_rc(c.CoreStartup(
            CORE_API_VERSION,
            <const char*>config_path_bytes if config_path is not None else NULL,
            <const char*>data_path_bytes if data_path is not None else NULL,
            <void *>self,
            _debug_callback,
            <void *>self,
            _state_callback
        ))
        self.open = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.open:
            check_rc(c.CoreShutdown())
            self.open = False

    def __dealloc__(self):
        self.close()

    def state_callback(self, param_type, new_value):
        pass

    def debug_callback(self, level, message):
        print(level, message)

