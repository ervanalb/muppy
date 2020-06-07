cimport cmupen64plus as c

def plugin_get_version():
    cdef c.m64p_plugin_type plugin_type
    cdef int plugin_version
    cdef int api_version
    cdef const char *plugin_name
    cdef int capabilities

    rv = c.PluginGetVersion(&plugin_type, &plugin_version, &api_version, &plugin_name, &capabilities)
    return (plugin_type, plugin_version, api_version, plugin_name, capabilities)
