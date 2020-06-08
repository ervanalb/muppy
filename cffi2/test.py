import mupen64plus

core = mupen64plus.Core()
input_plugin = mupen64plus.Plugin(core, "/usr/lib/mupen64plus/mupen64plus-input-sdl.so")
print(core.plugin_get_version())
print(input_plugin.plugin_get_version())
