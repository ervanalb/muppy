import subprocess
from cffi import FFI
ffi = FFI()




# Here, we use gcc -E to expand macros
# This gives us a definition of all of the exported symbols
# in a form that CFFI can understand
expanded_defs = subprocess.check_output(
    [
        "gcc",
        "-E",
        "mupen64plus_core.h",
    ]
)
expanded_defs = str(expanded_defs, encoding="utf8")

# Remove GCC __attribute__s
expanded_defs = expanded_defs.replace('__attribute__((visibility("default")))', "")

remove_words = ["PluginShutdown", "DebugCallback", "PluginStartup", "StateCallback"]

expanded_defs = "\n".join(l for l in expanded_defs.split("\n") if all(word not in l for word in remove_words))

ffibuilder.cdef(expanded_defs)

