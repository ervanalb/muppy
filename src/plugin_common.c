#define M64P_PLUGIN_PROTOTYPES 1
#include "mupen64plus/m64p_plugin.h"
#include "mupen64plus/m64p_types.h"

const int API_VERSION 0x20001
extern const m64p_plugin_type PLUGIN_TYPE; // Populated from each plugin

// Populated from Python
PyObject *handle;

static void *debug_context;
static ptr_DebugCallback debug_callback;

static const char* plugin_name;
static PyObject *plugin_name_obj; // Handles memory for plugin_name
static int plugin_version;

static m64p_error check_initialized() {
    if (handle == NULL) {
        debug_callback(debug_context, M64MSG_ERROR, "Attempting to use Python plugin from outside of Python");
        return M64ERR_INCOMPATIBLE;
    } else {
        return M64ERR_SUCCESS;
    }
}

static m64p_error py_callback_no_args(const char *function_name) {
    PyObject *obj = PyObject_GetAttrString(handle, function_name);
    if (obj != NULL) {
        PyObject *tup = PyTuple_New(0);
        if (tup != NULL) {
            PyObject_Call(obj, tup, NULL);
            Py_DECREF(tup);
            if (PyErr_Occurred()) {
                PyErr_Print();
                return M64ERR_INTERNAL;
            }
        } else {
            return M64ERR_MEMORY;
        }
    } else {
        debug_callback(debug_context, M64MSG_ERROR, "Could not find method");
        debug_callback(debug_context, M64MSG_ERROR, function_name);
        return M64ERR_INTERNAL;
    }
    return M64ERR_SUCCESS;
}

static char* get_bytes() {
}

m64p_error PluginStartup(m64p_dynlib_handle CoreLibHandle, void *Context, void (*DebugCallback)(void *Context, int level, const char *Message)) {
    (void)CoreLibHandle;

    debug_context = Context;
    debug_callback = DebugCallback;

    if (debug_callback == NULL) {
        return M64ERR_INPUT_ASSERT;
    }

    m64p_error rc = check_initialized();
    if (rc != M64ERR_SUCCESS) {
        return rc;
    }

    PyObject *obj = PyObject_GetAttrString(handle, "plugin_name");
    if (obj != NULL) {
        if (PyUnicode_Check(obj)) {
            plugin_name_obj = PyUnicode_AsEncodedString(result, "utf8", "strict"); // Owned reference
            if (plugin_name_obj != NULL) {
                plugin_name = PyBytes_AS_STRING(temp_bytes);
            } else {
                debug_callback(debug_context, M64MSG_ERROR, "Could not encode plugin_name");
                return M64ERR_INTERNAL;
            }
        } else {
            debug_callback(debug_context, M64MSG_ERROR, "plugin_name is not a string");
            return M64ERR_INTERNAL;
        }
    } else {
        debug_callback(debug_context, M64MSG_ERROR, "Could not find plugin_name");
        return M64ERR_INTERNAL;
    }

    PyObject *obj = PyObject_GetAttrString(handle, "plugin_version");
    if (obj != NULL) {
        plugin_version = PyLong_AsLong(obj);
        if (PyErr_Occurred()) {
            PyErr_Print();
            return M64ERR_INTERNAL;
        }
    } else {
        debug_callback(debug_context, M64MSG_ERROR, "Could not find plugin_version");
        return M64ERR_INTERNAL;
    }

    return py_callback_no_args("plugin_startup");
}

m64p_error PluginShutdown(void) {
    Py_XDECREF(plugin_name_obj);
    plugin_name_obj = NULL;

    m64p_error rc = check_initialized();
    if (rc != M64ERR_SUCCESS) {
        return rc;
    }

    rc = py_callback_no_args("plugin_shutdown");

    return rc;
}

m64p_error PluginGetVersion(m64p_plugin_type *PluginType, int *PluginVersion, int *APIVersion, const char **PluginNamePtr, int *Capabilities) {
    m64p_error rc = check_initialized();
    if (rc != M64ERR_SUCCESS) {
        return rc;
    }

    if (PluginType != NULL) {
        *PluginType = PLUGIN_TYPE;
    }

    if (PluginVersion != NULL) {
        *PluginVersion = py_plugin_version;
    }

    if (APIVersion != NULL) {
        *APIVersion = API_VERSION;
    }

    if (PluginNamePtr != NULL) {
        *PluginNamePtr = plugin_name;
    }

    return M64ERR_SUCCESS;
}

