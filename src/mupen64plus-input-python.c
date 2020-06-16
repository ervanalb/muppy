#include "plugin_common.c"

// Use this if debug_callback isn't working

//#define debug_callback fake_debug_callback

//static void fake_debug_callback(void *ctx, int lvl, char *msg) {
//    fprintf(stderr, "Fake debug: %s\n", msg);
//}

const m64p_plugin_type PLUGIN_TYPE = M64PLUGIN_INPUT;

void ControllerCommand(int Control, unsigned char *Command) {
}

void GetKeys(int Control, BUTTONS *Keys) {
    if (check_initialized() != M64ERR_SUCCESS) {
        return;
    }

    PyGILState_STATE gil = PyGILState_Ensure();

    PyObject *obj = NULL;
    PyObject *tup = NULL;
    PyObject *retval = NULL;

    obj = PyObject_GetAttrString(handle, "get_keys");
    if (obj != NULL) {
        PyObject *tup = Py_BuildValue("(i)", Control);
        if (tup != NULL) {
            retval = PyObject_Call(obj, tup, NULL);
            if (PyErr_Occurred()) {
                PyErr_Print();
                goto done;
            }
            if (retval == NULL) {
                debug_callback(debug_context, M64MSG_ERROR, "Missing return value");
                goto done;
            }
            int buttons = 0;
            int joy_x = 0;
            int joy_y = 0;
            if (PyArg_ParseTuple(retval, "iii", &buttons, &joy_x, &joy_y)) {
                uint32_t val = (buttons & 0xFFFF) | ((joy_x & 0xFF) << 16) | ((joy_y & 0xFF) << 24);
                Keys->Value = val;
            } else {
                debug_callback(debug_context, M64MSG_ERROR, "Didn't understand output of 'get_keys': Expected triple (buttons, x, y)");
                goto done;
            }
        } else {
            debug_callback(debug_context, M64MSG_ERROR, "Could not allocate tuple");
            goto done;
        }
    } else {
        debug_callback(debug_context, M64MSG_ERROR, "Could not find method 'get_keys'");
        
        goto done;
    }
done:
    Py_XDECREF(obj);
    obj = NULL;
    Py_XDECREF(tup);
    tup = NULL;
    Py_XDECREF(retval);
    retval = NULL;
    PyErr_Clear();
    PyGILState_Release(gil);
}

void InitiateControllers(CONTROL_INFO ControlInfo) {
    if (check_initialized() != M64ERR_SUCCESS) {
        return;
    }

    PyGILState_STATE gil = PyGILState_Ensure();

    PyObject *obj = NULL;
    PyObject *tup = NULL;
    PyObject *retval = NULL;

    obj = PyObject_GetAttrString(handle, "initiate_controllers");
    if (obj != NULL) {
        PyObject *tup = PyTuple_New(0);
        if (tup != NULL) {
            retval = PyObject_Call(obj, tup, NULL);
            if (PyErr_Occurred()) {
                PyErr_Print();
                goto done;
            }
            if (retval == NULL) {
                debug_callback(debug_context, M64MSG_ERROR, "Missing return value");
                goto done;
            }
            if (!PySequence_Check(retval)) {
                debug_callback(debug_context, M64MSG_ERROR, "Didn't understand output of 'initiate_controllers': Expected sequence");
                goto done;
            }
            int len = PySequence_Size(retval);
            if (len != 4) {
                debug_callback(debug_context, M64MSG_ERROR, "Didn't understand output of 'initiate_controllers': Expected sequence of length 4");
                goto done;
            }
            for (int i = 0; i < len; i++) {
                PyObject *item = PySequence_GetItem(retval, i);
                if (item == NULL) {
                    debug_callback(debug_context, M64MSG_ERROR, "Didn't understand output of 'initiate_controllers': Missing element");
                    goto done;
                }
                int present;
                int raw_data;
                int plugin;
                if (PyArg_ParseTuple(item, "ppp", &present, &raw_data, &plugin)) {
                    ControlInfo.Controls[i].Present = present;
                    ControlInfo.Controls[i].RawData = raw_data;
                    ControlInfo.Controls[i].Plugin = plugin;
                } else {
                    debug_callback(debug_context, M64MSG_ERROR, "Didn't understand output of 'initiate_controllers': Expected element to be a triple (present, raw_data, plugin)");
                    goto done;
                }
            }
        } else {
            debug_callback(debug_context, M64MSG_ERROR, "Could not allocate tuple");
            goto done;
        }
    } else {
        debug_callback(debug_context, M64MSG_ERROR, "Could not find method 'initiate_controllers'");
        goto done;
    }
done:
    Py_XDECREF(obj);
    obj = NULL;
    Py_XDECREF(tup);
    tup = NULL;
    Py_XDECREF(retval);
    retval = NULL;
    PyErr_Clear();
    PyGILState_Release(gil);
}

void ReadController(int Control, unsigned char *Command) {
}

int RomOpen(void) {
}

void RomClosed(void) {
}

void SDL_KeyDown(int keymod, int keysym) {
}

void SDL_KeyUp(int keymod, int keysym) {
}
