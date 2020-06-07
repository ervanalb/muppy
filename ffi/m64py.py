import subprocess
from cffi import FFI
ffibuilder = FFI()

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

print(expanded_defs)

expanded_defs = "\n".join(l for l in expanded_defs.split("\n") if all(word not in l for word in remove_words))

ffibuilder.cdef(expanded_defs)

# set_source() gives the name of the python extension module to
# produce, and some C source code as a string.  This C code needs
# to make the declarated functions, types and globals available,
# so it is often just the "#include".
ffibuilder.set_source("_m64",
    """
    #include "mupen64plus_core.h"
    """,
    libraries = ['mupen64plus'],
    extra_compile_args = [
        "-I",
        "..",
    ],
)

if __name__ == "__main__":
    ffibuilder.compile(tmpdir="cffi_tmp", verbose=True)
    import cffi_tmp._m64
