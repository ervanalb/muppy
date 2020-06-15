from cffi import FFI
from enum import IntEnum, IntFlag
from collections import namedtuple
from typing import Optional
import ctypes, ctypes.util
import logging
import os
import pkg_resources
import inspect

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

    def __init__(self, config_path: Optional[str]=None, data_path: Optional[str]=None, dl: Optional[str]=None):
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

    def close(self):
        if self.open:
            check_rc(self.handle.CoreShutdown())
            self.open = False
        super().close()

    def state_callback(self, param_type, new_value):
        pass

    def debug_callback(self, level, message):
        loglvl = LOGLEVEL.get(level, logging.NOTSET)
        logger.log(loglvl, message)

    def rom_open(self, rom: bytes):
        check_rc(self.handle.CoreDoCommand(Command.ROM_OPEN, len(rom), rom))

    def rom_close(self):
        check_rc(self.handle.CoreDoCommand(Command.ROM_CLOSE, 0, ffi.NULL))

    def attach_plugin(self, plugin: "Plugin"):
        check_rc(self.handle.CoreAttachPlugin(plugin.version.plugin_type, plugin.handle_raw))
        self.plugins.append(plugin)

    def detach_plugin(self, plugin: "Plugin"):
        if plugin not in self.plugins:
            raise ValueError("Plugin not attached")
        check_rc(self.handle.CoreDetachPlugin(plugin.version.plugin_type))
        self.plugins.remove(plugin)

    def detach_plugins(self):
        attached_plugins = list(reversed(self.plugins))
        for plugin in attached_plugins:
            self.detach_plugin(plugin)

    def auto_attach_plugins(self, video_plugin=None, audio_plugin=None, input_plugin=None, rsp_plugin=None):
        section = ffi.new("m64p_handle *")
        check_rc(self.handle.ConfigOpenSection(b"UI-Console", section))
        static_string = ffi.new("char[1024]")

        rc = self.handle.ConfigGetParameter(section[0], b"PluginDir", Type.STRING, static_string, 1024)
        if rc == Error.SUCCESS:
            plugin_dir = str(ffi.string(static_string), encoding="utf8")
        elif rc == Error.INPUT_INVALID:
            plugin_dir = ""
        else:
            check_rc(rc)

        overrides = {
            "VideoPlugin": video_plugin,
            "AudioPlugin": audio_plugin,
            "InputPlugin": input_plugin,
            "RspPlugin": rsp_plugin,
        }

        def get_plugin(plugin_name):
            custom = overrides.get(plugin_name)
            if custom is not None:
                if isinstance(custom, str):
                    plugin_path = os.path.abspath(os.path.join(plugin_dir, custom))
                    return Plugin(self, dl=plugin_path)
                elif inspect.isclass(custom):
                    return custom(self)
                else:
                    return custom

            rc = self.handle.ConfigGetParameter(section[0], bytes(plugin_name, encoding="latin1"), Type.STRING, static_string, 1024)
            if rc == Error.SUCCESS:
                plugin_path = os.path.abspath(os.path.join(plugin_dir, str(ffi.string(static_string), encoding="utf8")))
            elif rc == Error.INPUT_INVALID:
                plugin_path = ""
            else:
                check_rc(rc)

            if plugin_path != "":
                logger.info("Attaching {} {}".format(plugin_name, plugin_path))
                return Plugin(self, dl=plugin_path)
            else:
                logger.warning("Could not find {0} in UI-Console section of config, not attaching {0}".format(plugin_name))

        plugins = [get_plugin(n) for n in ["VideoPlugin", "AudioPlugin", "InputPlugin", "RspPlugin"]]
        for plugin in plugins:
            self.attach_plugin(plugin)

        self.video_plugin, self.audio_plugin, self.input_plugin, self.rsp_plugin = plugins

    def execute(self):
        check_rc(self.handle.CoreDoCommand(Command.EXECUTE, 0, ffi.NULL))

    def stop(self):
        check_rc(self.handle.CoreDoCommand(Command.STOP, 0, ffi.NULL))

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
