#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define M64P_PLUGIN_PROTOTYPES 1
#include "mupen64plus/m64p_common.h"
#include "mupen64plus/m64p_frontend.h"
#include "mupen64plus/m64p_plugin.h"
#include "mupen64plus/m64p_types.h"

const int API_VERSION = 0x020100;
extern const m64p_plugin_type PLUGIN_TYPE; // Populated from each plugin

// Populated from Python
PyObject *handle;

static void *debug_context;
static ptr_DebugCallback debug_callback;

static const char* plugin_name;
static PyObject *plugin_name_obj; // Handles memory for plugin_name
static int plugin_version;

static m64p_error check_initialized() {
    if (handle == NULL || !Py_IsInitialized()) {
        if (debug_callback != NULL) {
            debug_callback(debug_context, M64MSG_ERROR, "Attempting to use Python plugin from outside of Python");
        } else {
            fprintf(stderr, "Attempting to use Python plugin from outside of Python\n");
        }
        return M64ERR_INCOMPATIBLE;
    } else {
        return M64ERR_SUCCESS;
    }
}

m64p_error PluginStartup(m64p_dynlib_handle CoreLibHandle, void *Context, void (*DebugCallback)(void *Context, int level, const char *Message)) {
    (void)CoreLibHandle;

    m64p_error rc = M64ERR_SUCCESS;

    PyGILState_STATE gil = PyGILState_Ensure();

    debug_context = Context;
    debug_callback = DebugCallback;

    Py_INCREF(handle);

    if (debug_callback == NULL) {
        rc = M64ERR_INPUT_ASSERT;
        goto done;
    }

    rc = check_initialized();
    if (rc != M64ERR_SUCCESS) {
        goto done;
    }

    PyObject *obj = PyObject_GetAttrString(handle, "plugin_name");
    if (obj != NULL) {
        if (PyUnicode_Check(obj)) {
            plugin_name_obj = PyUnicode_AsEncodedString(obj, "utf8", "strict"); // Owned reference
            if (plugin_name_obj != NULL) {
                plugin_name = PyBytes_AS_STRING(plugin_name_obj);
            } else {
                debug_callback(debug_context, M64MSG_ERROR, "Could not encode plugin_name");
                rc = M64ERR_INTERNAL;
                goto done;
            }
        } else {
            debug_callback(debug_context, M64MSG_ERROR, "plugin_name is not a string");
            rc = M64ERR_INTERNAL;
            goto done;
        }
    } else {
        debug_callback(debug_context, M64MSG_ERROR, "Could not find plugin_name");
        rc = M64ERR_INTERNAL;
        goto done;
    }

    obj = PyObject_GetAttrString(handle, "plugin_version");
    if (obj != NULL) {
        plugin_version = PyLong_AsLong(obj);
        if (PyErr_Occurred()) {
            PyErr_Print();
            rc = M64ERR_INTERNAL;
            goto done;
        }
    } else {
        debug_callback(debug_context, M64MSG_ERROR, "Could not find plugin_version");
        rc = M64ERR_INTERNAL;
        goto done;
    }

done:
    PyErr_Clear();
    PyGILState_Release(gil);
    return rc;
}

m64p_error PluginShutdown(void) {
    m64p_error rc = M64ERR_SUCCESS;
    PyGILState_STATE gil = PyGILState_Ensure();

    Py_XDECREF(plugin_name_obj);
    plugin_name_obj = NULL;

    Py_XDECREF(handle);
    handle = NULL;

    rc = check_initialized();
    if (rc != M64ERR_SUCCESS) {
        goto done;
    }

done:
    PyErr_Clear();
    PyGILState_Release(gil);
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
        *PluginVersion = plugin_version;
    }

    if (APIVersion != NULL) {
        *APIVersion = API_VERSION;
    }

    if (PluginNamePtr != NULL) {
        *PluginNamePtr = plugin_name;
    }

    return M64ERR_SUCCESS;
}

