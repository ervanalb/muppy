cimport cmupen64plus as c
from enum import Enum, Flag
from collections import namedtuple

class Mupen64PlusError(Exception):
    pass

def check_rc(rc):
    if rc == c.M64ERR_SUCCESS:
        return

    raise {
        c.M64ERR_NOT_INIT: Mupen64PlusError("Not initialized"),
        c.M64ERR_ALREADY_INIT: Mupen64PlusError("Already initialized"),
        c.M64ERR_INCOMPATIBLE: Mupen64PlusError("Incompatible"),
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
