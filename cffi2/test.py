import mupen64plus

core = mupen64plus.Core(dl="/home/eric/Downloads/mupen64plus-git/src/mupen64plus-core/projects/unix/libmupen64plus.so.2.0.0")
input_plugin = mupen64plus.Plugin(core, "/usr/lib/mupen64plus/mupen64plus-input-sdl.so")
video_plugin = mupen64plus.Plugin(core, "/usr/lib/mupen64plus/mupen64plus-video-glide64mk2.so")
rsp_plugin = mupen64plus.Plugin(core, "/usr/lib/mupen64plus/mupen64plus-rsp-hle.so")
audio_plugin = mupen64plus.Plugin(core, "/usr/lib/mupen64plus/mupen64plus-audio-sdl.so")

print(core.plugin_get_version())

rom = open("/home/eric/sm64/baserom.jp.z64", "rb").read()
core.rom_open(rom)
core.rom_close()
