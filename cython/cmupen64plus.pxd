cdef extern from "mupen64plus_core.h":

    #ctypedef void * m64p_dynlib_handle;
    #ctypedef void * m64p_handle;
    #ctypedef void (*m64p_function)();

    #ctypedef void (*m64p_frame_callback)(unsigned int FrameIndex);
    #ctypedef void (*m64p_input_callback)();
    #ctypedef void (*m64p_audio_callback)();
    #ctypedef void (*m64p_vi_callback)();

    #ctypedef enum m64p_type:
    #    M64TYPE_INT = 1,
    #    M64TYPE_FLOAT,
    #    M64TYPE_BOOL,
    #    M64TYPE_STRING

    #ctypedef enum m64p_msg_level:
    #    M64MSG_ERROR = 1,
    #    M64MSG_WARNING,
    #    M64MSG_INFO,
    #    M64MSG_STATUS,
    #    M64MSG_VERBOSE

    ctypedef enum m64p_error:
        M64ERR_SUCCESS = 0,
        M64ERR_NOT_INIT,
        M64ERR_ALREADY_INIT,
        M64ERR_INCOMPATIBLE,
        M64ERR_INPUT_ASSERT,
        M64ERR_INPUT_INVALID,
        M64ERR_INPUT_NOT_FOUND,
        M64ERR_NO_MEMORY,
        M64ERR_FILES,
        M64ERR_INTERNAL,
        M64ERR_INVALID_STATE,
        M64ERR_PLUGIN_FAIL,
        M64ERR_SYSTEM_FAIL,
        M64ERR_UNSUPPORTED,
        M64ERR_WRONG_TYPE

    ctypedef enum m64p_core_caps:
        M64CAPS_DYNAREC = 1,
        M64CAPS_DEBUGGER = 2,
        M64CAPS_CORE_COMPARE = 4

    ctypedef enum m64p_plugin_type:
        M64PLUGIN_NULL = 0,
        M64PLUGIN_RSP = 1,
        M64PLUGIN_GFX,
        M64PLUGIN_AUDIO,
        M64PLUGIN_INPUT,
        M64PLUGIN_CORE

    #ctypedef enum m64p_emu_state:
    #    M64EMU_STOPPED = 1,
    #    M64EMU_RUNNING,
    #    M64EMU_PAUSED

    #ctypedef enum m64p_video_mode:
    #    M64VIDEO_NONE = 1,
    #    M64VIDEO_WINDOWED,
    #    M64VIDEO_FULLSCREEN

    #ctypedef enum m64p_video_flags:
    #    M64VIDEOFLAG_SUPPORT_RESIZING = 1

    #ctypedef enum m64p_core_param:
    #    M64CORE_EMU_STATE = 1,
    #    M64CORE_VIDEO_MODE,
    #    M64CORE_SAVESTATE_SLOT,
    #    M64CORE_SPEED_FACTOR,
    #    M64CORE_SPEED_LIMITER,
    #    M64CORE_VIDEO_SIZE,
    #    M64CORE_AUDIO_VOLUME,
    #    M64CORE_AUDIO_MUTE,
    #    M64CORE_INPUT_GAMESHARK,
    #    M64CORE_STATE_LOADCOMPLETE,
    #    M64CORE_STATE_SAVECOMPLETE

    #ctypedef enum m64p_command:
    #    M64CMD_NOP = 0,
    #    M64CMD_ROM_OPEN,
    #    M64CMD_ROM_CLOSE,
    #    M64CMD_ROM_GET_HEADER,
    #    M64CMD_ROM_GET_SETTINGS,
    #    M64CMD_EXECUTE,
    #    M64CMD_STOP,
    #    M64CMD_PAUSE,
    #    M64CMD_RESUME,
    #    M64CMD_CORE_STATE_QUERY,
    #    M64CMD_STATE_LOAD,
    #    M64CMD_STATE_SAVE,
    #    M64CMD_STATE_SET_SLOT,
    #    M64CMD_SEND_SDL_KEYDOWN,
    #    M64CMD_SEND_SDL_KEYUP,
    #    M64CMD_SET_FRAME_CALLBACK,
    #    M64CMD_TAKE_NEXT_SCREENSHOT,
    #    M64CMD_CORE_STATE_SET,
    #    M64CMD_READ_SCREEN,
    #    M64CMD_RESET,
    #    M64CMD_ADVANCE_FRAME,
    #    M64CMD_SET_MEDIA_LOADER

    #ctypedef struct m64p_cheat_code:
    #    uint32_t address;
    #    int value;

    #ctypedef struct m64p_media_loader:
    #    void* cb_data;
    #    char* (*get_gb_cart_rom)(void* cb_data, int controller_num);
    #    char* (*get_gb_cart_ram)(void* cb_data, int controller_num);
    #    char* (*get_dd_rom)(void* cb_data);
    #    char* (*get_dd_disk)(void* cb_data);

    #ctypedef enum m64p_system_type:
    #    SYSTEM_NTSC = 0,
    #    SYSTEM_PAL,
    #    SYSTEM_MPAL

    #ctypedef struct m64p_rom_header:
    #    uint8_t init_PI_BSB_DOM1_LAT_REG;
    #    uint8_t init_PI_BSB_DOM1_PGS_REG;
    #    uint8_t init_PI_BSB_DOM1_PWD_REG;
    #    uint8_t init_PI_BSB_DOM1_PGS_REG2;
    #    uint32_t ClockRate;
    #    uint32_t PC;
    #    uint32_t Release;
    #    uint32_t CRC1;
    #    uint32_t CRC2;
    #    uint32_t Unknown[2];
    #    uint8_t Name[20];
    #    uint32_t unknown;
    #    uint32_t Manufacturer_ID;
    #    uint16_t Cartridge_ID;
    #    uint16_t Country_code;

    #ctypedef struct m64p_rom_settings:
    #    char goodname[256];
    #    char MD5[33];
    #    unsigned char savetype;
    #    unsigned char status;
    #    unsigned char players;
    #    unsigned char rumble;
    #    unsigned char transferpak;
    #    unsigned char mempak;
    #    unsigned char biopak;

    #ctypedef enum m64p_dbg_state:
    #    M64P_DBG_RUN_STATE = 1,
    #    M64P_DBG_PREVIOUS_PC,
    #    M64P_DBG_NUM_BREAKPOINTS,
    #    M64P_DBG_CPU_DYNACORE,
    #    M64P_DBG_CPU_NEXT_INTERRUPT

    #ctypedef enum m64p_dbg_runstate:
    #    M64P_DBG_RUNSTATE_PAUSED = 0,
    #    M64P_DBG_RUNSTATE_STEPPING,
    #    M64P_DBG_RUNSTATE_RUNNING

    #ctypedef enum m64p_dbg_mem_info:
    #    M64P_DBG_MEM_TYPE = 1,
    #    M64P_DBG_MEM_FLAGS,
    #    M64P_DBG_MEM_HAS_RECOMPILED,
    #    M64P_DBG_MEM_NUM_RECOMPILED,
    #    M64P_DBG_RECOMP_OPCODE = 16,
    #    M64P_DBG_RECOMP_ARGS,
    #    M64P_DBG_RECOMP_ADDR

    #ctypedef enum m64p_dbg_mem_type:
    #    M64P_MEM_NOMEM = 0,
    #    M64P_MEM_NOTHING,
    #    M64P_MEM_RDRAM,
    #    M64P_MEM_RDRAMREG,
    #    M64P_MEM_RSPMEM,
    #    M64P_MEM_RSPREG,
    #    M64P_MEM_RSP,
    #    M64P_MEM_DP,
    #    M64P_MEM_DPS,
    #    M64P_MEM_VI,
    #    M64P_MEM_AI,
    #    M64P_MEM_PI,
    #    M64P_MEM_RI,
    #    M64P_MEM_SI,
    #    M64P_MEM_FLASHRAMSTAT,
    #    M64P_MEM_ROM,
    #    M64P_MEM_PIF,
    #    M64P_MEM_MI,
    #    M64P_MEM_BREAKPOINT

    #ctypedef enum m64p_dbg_mem_flags:
    #    M64P_MEM_FLAG_READABLE = 0x01,
    #    M64P_MEM_FLAG_WRITABLE = 0x02,
    #    M64P_MEM_FLAG_READABLE_EMUONLY = 0x04,
    #    M64P_MEM_FLAG_WRITABLE_EMUONLY = 0x08

    #ctypedef enum m64p_dbg_memptr_type:
    #    M64P_DBG_PTR_RDRAM = 1,
    #    M64P_DBG_PTR_PI_REG,
    #    M64P_DBG_PTR_SI_REG,
    #    M64P_DBG_PTR_VI_REG,
    #    M64P_DBG_PTR_RI_REG,
    #    M64P_DBG_PTR_AI_REG

    #ctypedef enum m64p_dbg_cpu_data:
    #    M64P_CPU_PC = 1,
    #    M64P_CPU_REG_REG,
    #    M64P_CPU_REG_HI,
    #    M64P_CPU_REG_LO,
    #    M64P_CPU_REG_COP0,
    #    M64P_CPU_REG_COP1_DOUBLE_PTR,
    #    M64P_CPU_REG_COP1_SIMPLE_PTR,
    #    M64P_CPU_REG_COP1_FGR_64,
    #    M64P_CPU_TLB

    #ctypedef enum m64p_dbg_bkp_command:
    #    M64P_BKP_CMD_ADD_ADDR = 1,
    #    M64P_BKP_CMD_ADD_STRUCT,
    #    M64P_BKP_CMD_REPLACE,
    #    M64P_BKP_CMD_REMOVE_ADDR,
    #    M64P_BKP_CMD_REMOVE_IDX,
    #    M64P_BKP_CMD_ENABLE,
    #    M64P_BKP_CMD_DISABLE,
    #    M64P_BKP_CMD_CHECK

    #ctypedef enum m64p_dbg_bkp_flags:
    #    M64P_BKP_FLAG_ENABLED = 0x01,
    #    M64P_BKP_FLAG_READ = 0x02,
    #    M64P_BKP_FLAG_WRITE = 0x04,
    #    M64P_BKP_FLAG_EXEC = 0x08,
    #    M64P_BKP_FLAG_LOG = 0x10

    #ctypedef struct m64p_breakpoint:
    #    uint32_t address;
    #    uint32_t endaddr;
    #    unsigned int flags;

    #ctypedef struct m64p_2d_size:
    #    unsigned int uiWidth;
    #    unsigned int uiHeight;

    #ctypedef enum m64p_GLattr:
    #    M64P_GL_DOUBLEBUFFER = 1,
    #    M64P_GL_BUFFER_SIZE,
    #    M64P_GL_DEPTH_SIZE,
    #    M64P_GL_RED_SIZE,
    #    M64P_GL_GREEN_SIZE,
    #    M64P_GL_BLUE_SIZE,
    #    M64P_GL_ALPHA_SIZE,
    #    M64P_GL_SWAP_CONTROL,
    #    M64P_GL_MULTISAMPLEBUFFERS,
    #    M64P_GL_MULTISAMPLESAMPLES,
    #    M64P_GL_CONTEXT_MAJOR_VERSION,
    #    M64P_GL_CONTEXT_MINOR_VERSION,
    #    M64P_GL_CONTEXT_PROFILE_MASK

    #ctypedef enum m64p_GLContextType:
    #    M64P_GL_CONTEXT_PROFILE_CORE,
    #    M64P_GL_CONTEXT_PROFILE_COMPATIBILITY,
    #    M64P_GL_CONTEXT_PROFILE_ES

    #ctypedef struct m64p_video_extension_functions:
    #    unsigned int Functions;
    #    m64p_error (*VidExtFuncInit)();
    #    m64p_error (*VidExtFuncQuit)();
    #    m64p_error (*VidExtFuncListModes)(m64p_2d_size *, int *);
    #    m64p_error (*VidExtFuncSetMode)(int, int, int, int, int);
    #    m64p_function (*VidExtFuncGLGetProc)(const char*);
    #    m64p_error (*VidExtFuncGLSetAttr)(m64p_GLattr, int);
    #    m64p_error (*VidExtFuncGLGetAttr)(m64p_GLattr, int *);
    #    m64p_error (*VidExtFuncGLSwapBuf)();
    #    m64p_error (*VidExtFuncSetCaption)(const char *);
    #    m64p_error (*VidExtFuncToggleFS)();
    #    m64p_error (*VidExtFuncResizeWindow)(int, int);
    #    uint32_t (*VidExtFuncGLGetDefaultFramebuffer)();

    #ctypedef m64p_error (*ptr_PluginGetVersion)(m64p_plugin_type *, int *, int *, const char **, int *);
    m64p_error PluginGetVersion(m64p_plugin_type *, int *, int *, const char **, int *)

    #ctypedef m64p_error (*ptr_CoreGetAPIVersions)(int *, int *, int *, int *);
    #m64p_error CoreGetAPIVersions(int *, int *, int *, int *);

    #ctypedef const char * (*ptr_CoreErrorMessage)(m64p_error);
    #const char * CoreErrorMessage(m64p_error);

    #ctypedef m64p_error (*ptr_PluginStartup)(m64p_dynlib_handle, void *, void (*)(void *, int, const char *));
    #m64p_error PluginStartup(m64p_dynlib_handle, void *, void (*)(void *, int, const char *));

    #ctypedef m64p_error (*ptr_PluginShutdown)();
    #m64p_error PluginShutdown();

    #ctypedef m64p_error (*ptr_DebugSetCallbacks)(void (*)(), void (*)(unsigned int), void (*)());
    #m64p_error DebugSetCallbacks(void (*)(), void (*)(unsigned int), void (*)());

    #ctypedef m64p_error (*ptr_DebugSetCoreCompare)(void (*)(unsigned int), void (*)(int, void *));
    #m64p_error DebugSetCoreCompare(void (*)(unsigned int), void (*)(int, void *));

    #ctypedef m64p_error (*ptr_DebugSetRunState)(m64p_dbg_runstate);
    #m64p_error DebugSetRunState(m64p_dbg_runstate);

    #ctypedef int (*ptr_DebugGetState)(m64p_dbg_state);
    #int DebugGetState(m64p_dbg_state);

    #ctypedef m64p_error (*ptr_DebugStep)();
    #m64p_error DebugStep();

    #ctypedef void (*ptr_DebugDecodeOp)(unsigned int, char *, char *, int);
    #void DebugDecodeOp(unsigned int, char *, char *, int);

    #ctypedef void * (*ptr_DebugMemGetRecompInfo)(m64p_dbg_mem_info, unsigned int, int);
    #void * DebugMemGetRecompInfo(m64p_dbg_mem_info, unsigned int, int);

    #ctypedef int (*ptr_DebugMemGetMemInfo)(m64p_dbg_mem_info, unsigned int);
    #int DebugMemGetMemInfo(m64p_dbg_mem_info, unsigned int);

    #ctypedef void * (*ptr_DebugMemGetPointer)(m64p_dbg_memptr_type);
    #void * DebugMemGetPointer(m64p_dbg_memptr_type);

#typedef unsigned long long (*ptr_DebugMemRead64)(unsigned int);
#typedef unsigned int (*ptr_DebugMemRead32)(unsigned int);
#typedef unsigned short (*ptr_DebugMemRead16)(unsigned int);
#typedef unsigned char (*ptr_DebugMemRead8)(unsigned int);
#
#unsigned long long DebugMemRead64(unsigned int);
#unsigned int DebugMemRead32(unsigned int);
#unsigned short DebugMemRead16(unsigned int);
#unsigned char DebugMemRead8(unsigned int);
#
#typedef void (*ptr_DebugMemWrite64)(unsigned int, unsigned long long);
#typedef void (*ptr_DebugMemWrite32)(unsigned int, unsigned int);
#typedef void (*ptr_DebugMemWrite16)(unsigned int, unsigned short);
#typedef void (*ptr_DebugMemWrite8)(unsigned int, unsigned char);
#
#void DebugMemWrite64(unsigned int, unsigned long long);
#void DebugMemWrite32(unsigned int, unsigned int);
#void DebugMemWrite16(unsigned int, unsigned short);
#void DebugMemWrite8(unsigned int, unsigned char);
#
#typedef void * (*ptr_DebugGetCPUDataPtr)(m64p_dbg_cpu_data);
#void * DebugGetCPUDataPtr(m64p_dbg_cpu_data);
#
#typedef int (*ptr_DebugBreakpointLookup)(unsigned int, unsigned int, unsigned int);
#int DebugBreakpointLookup(unsigned int, unsigned int, unsigned int);
#
#typedef int (*ptr_DebugBreakpointCommand)(m64p_dbg_bkp_command, unsigned int, m64p_breakpoint *);
#int DebugBreakpointCommand(m64p_dbg_bkp_command, unsigned int, m64p_breakpoint *);
#
#typedef void (*ptr_DebugBreakpointTriggeredBy)(uint32_t *, uint32_t *);
#void DebugBreakpointTriggeredBy(uint32_t *, uint32_t *);
#
#typedef uint32_t (*ptr_DebugVirtualToPhysical)(uint32_t);
#uint32_t DebugVirtualToPhysical(uint32_t);
#
#typedef struct {
#    unsigned char * RDRAM;
#    unsigned char * DMEM;
#    unsigned char * IMEM;
#
#    unsigned int * MI_INTR_REG;
#
#    unsigned int * SP_MEM_ADDR_REG;
#    unsigned int * SP_DRAM_ADDR_REG;
#    unsigned int * SP_RD_LEN_REG;
#    unsigned int * SP_WR_LEN_REG;
#    unsigned int * SP_STATUS_REG;
#    unsigned int * SP_DMA_FULL_REG;
#    unsigned int * SP_DMA_BUSY_REG;
#    unsigned int * SP_PC_REG;
#    unsigned int * SP_SEMAPHORE_REG;
#
#    unsigned int * DPC_START_REG;
#    unsigned int * DPC_END_REG;
#    unsigned int * DPC_CURRENT_REG;
#    unsigned int * DPC_STATUS_REG;
#    unsigned int * DPC_CLOCK_REG;
#    unsigned int * DPC_BUFBUSY_REG;
#    unsigned int * DPC_PIPEBUSY_REG;
#    unsigned int * DPC_TMEM_REG;
#
#    void (*CheckInterrupts)(void);
#    void (*ProcessDlistList)(void);
#    void (*ProcessAlistList)(void);
#    void (*ProcessRdpList)(void);
#    void (*ShowCFB)(void);
#} RSP_INFO;
#
#typedef struct {
#    unsigned char * HEADER;
#    unsigned char * RDRAM;
#    unsigned char * DMEM;
#    unsigned char * IMEM;
#
#    unsigned int * MI_INTR_REG;
#
#    unsigned int * DPC_START_REG;
#    unsigned int * DPC_END_REG;
#    unsigned int * DPC_CURRENT_REG;
#    unsigned int * DPC_STATUS_REG;
#    unsigned int * DPC_CLOCK_REG;
#    unsigned int * DPC_BUFBUSY_REG;
#    unsigned int * DPC_PIPEBUSY_REG;
#    unsigned int * DPC_TMEM_REG;
#
#    unsigned int * VI_STATUS_REG;
#    unsigned int * VI_ORIGIN_REG;
#    unsigned int * VI_WIDTH_REG;
#    unsigned int * VI_INTR_REG;
#    unsigned int * VI_V_CURRENT_LINE_REG;
#    unsigned int * VI_TIMING_REG;
#    unsigned int * VI_V_SYNC_REG;
#    unsigned int * VI_H_SYNC_REG;
#    unsigned int * VI_LEAP_REG;
#    unsigned int * VI_H_START_REG;
#    unsigned int * VI_V_START_REG;
#    unsigned int * VI_V_BURST_REG;
#    unsigned int * VI_X_SCALE_REG;
#    unsigned int * VI_Y_SCALE_REG;
#
#    void (*CheckInterrupts)(void);
#    unsigned int version;
#    unsigned int * SP_STATUS_REG;
#    const unsigned int * RDRAM_SIZE;
#} GFX_INFO;
#
#typedef struct {
#    unsigned char * RDRAM;
#    unsigned char * DMEM;
#    unsigned char * IMEM;
#
#    unsigned int * MI_INTR_REG;
#
#    unsigned int * AI_DRAM_ADDR_REG;
#    unsigned int * AI_LEN_REG;
#    unsigned int * AI_CONTROL_REG;
#    unsigned int * AI_STATUS_REG;
#    unsigned int * AI_DACRATE_REG;
#    unsigned int * AI_BITRATE_REG;
#
#    void (*CheckInterrupts)(void);
#} AUDIO_INFO;
#
#typedef struct {
#    int Present;
#    int RawData;
#    int Plugin;
#} CONTROL;
#
#typedef union {
#    unsigned int Value;
#    struct {
#        unsigned R_DPAD : 1;
#        unsigned L_DPAD : 1;
#        unsigned D_DPAD : 1;
#        unsigned U_DPAD : 1;
#        unsigned START_BUTTON : 1;
#        unsigned Z_TRIG : 1;
#        unsigned B_BUTTON : 1;
#        unsigned A_BUTTON : 1;
#
#        unsigned R_CBUTTON : 1;
#        unsigned L_CBUTTON : 1;
#        unsigned D_CBUTTON : 1;
#        unsigned U_CBUTTON : 1;
#        unsigned R_TRIG : 1;
#        unsigned L_TRIG : 1;
#        unsigned Reserved1 : 1;
#        unsigned Reserved2 : 1;
#
#        signed X_AXIS : 8;
#        signed Y_AXIS : 8;
#    };
#} BUTTONS;
#
#typedef struct {
#    CONTROL *Controls;
#
#} CONTROL_INFO;
#
#
#typedef void (*ptr_RomClosed)(void);
#typedef int (*ptr_RomOpen)(void);
#typedef void (*ptr_ChangeWindow)(void);
#typedef int (*ptr_InitiateGFX)(GFX_INFO Gfx_Info);
#typedef void (*ptr_MoveScreen)(int x, int y);
#typedef void (*ptr_ProcessDList)(void);
#typedef void (*ptr_ProcessRDPList)(void);
#typedef void (*ptr_ShowCFB)(void);
#typedef void (*ptr_UpdateScreen)(void);
#typedef void (*ptr_ViStatusChanged)(void);
#typedef void (*ptr_ViWidthChanged)(void);
#typedef void (*ptr_ReadScreen2)(void *dest, int *width, int *height, int front);
#typedef void (*ptr_SetRenderingCallback)(void (*callback)(int));
#typedef void (*ptr_ResizeVideoOutput)(int width, int height);
#
#typedef struct
#{
#   unsigned int addr;
#   unsigned int size;
#   unsigned int width;
#   unsigned int height;
#} FrameBufferInfo;
#typedef void (*ptr_FBRead)(unsigned int addr);
#typedef void (*ptr_FBWrite)(unsigned int addr, unsigned int size);
#typedef void (*ptr_FBGetFrameBufferInfo)(void *p);
#
#typedef void (*ptr_AiDacrateChanged)(int SystemType);
#typedef void (*ptr_AiLenChanged)(void);
#typedef int (*ptr_InitiateAudio)(AUDIO_INFO Audio_Info);
#typedef void (*ptr_ProcessAList)(void);
#typedef void (*ptr_SetSpeedFactor)(int percent);
#typedef void (*ptr_VolumeUp)(void);
#typedef void (*ptr_VolumeDown)(void);
#typedef int (*ptr_VolumeGetLevel)(void);
#typedef void (*ptr_VolumeSetLevel)(int level);
#typedef void (*ptr_VolumeMute)(void);
#typedef const char * (*ptr_VolumeGetString)(void);
#
#typedef void (*ptr_ControllerCommand)(int Control, unsigned char *Command);
#typedef void (*ptr_GetKeys)(int Control, BUTTONS *Keys);
#typedef void (*ptr_InitiateControllers)(CONTROL_INFO ControlInfo);
#typedef void (*ptr_ReadController)(int Control, unsigned char *Command);
#typedef void (*ptr_SDL_KeyDown)(int keymod, int keysym);
#typedef void (*ptr_SDL_KeyUp)(int keymod, int keysym);
#typedef void (*ptr_RenderCallback)(void);
#
#typedef unsigned int (*ptr_DoRspCycles)(unsigned int Cycles);
#typedef void (*ptr_InitiateRSP)(RSP_INFO Rsp_Info, unsigned int *CycleCount);
#
#typedef m64p_error (*ptr_VidExt_Init)(void);
#m64p_error VidExt_Init(void);
#
#typedef m64p_error (*ptr_VidExt_Quit)(void);
#m64p_error VidExt_Quit(void);
#
#typedef m64p_error (*ptr_VidExt_ListFullscreenModes)(m64p_2d_size *, int *);
#m64p_error VidExt_ListFullscreenModes(m64p_2d_size *, int *);
#
#typedef m64p_error (*ptr_VidExt_SetVideoMode)(int, int, int, m64p_video_mode, m64p_video_flags);
#
#m64p_error VidExt_SetVideoMode(int, int, int, m64p_video_mode, m64p_video_flags);
#
#typedef m64p_error (*ptr_VidExt_ResizeWindow)(int, int);
#m64p_error VidExt_ResizeWindow(int, int);
#
#typedef m64p_error (*ptr_VidExt_SetCaption)(const char *);
#m64p_error VidExt_SetCaption(const char *);
#
#typedef m64p_error (*ptr_VidExt_ToggleFullScreen)(void);
#m64p_error VidExt_ToggleFullScreen(void);
#
#typedef m64p_function (*ptr_VidExt_GL_GetProcAddress)(const char *);
#m64p_function VidExt_GL_GetProcAddress(const char *);
#
#typedef m64p_error (*ptr_VidExt_GL_SetAttribute)(m64p_GLattr, int);
#m64p_error VidExt_GL_SetAttribute(m64p_GLattr, int);
#
#typedef m64p_error (*ptr_VidExt_GL_GetAttribute)(m64p_GLattr, int *);
#m64p_error VidExt_GL_GetAttribute(m64p_GLattr, int *);
#
#typedef m64p_error (*ptr_VidExt_GL_SwapBuffers)(void);
#m64p_error VidExt_GL_SwapBuffers(void);
#
#typedef uint32_t (*ptr_VidExt_GL_GetDefaultFramebuffer)(void);
#uint32_t VidExt_GL_GetDefaultFramebuffer(void);
#
#typedef m64p_error (*ptr_ConfigListSections)(void *, void (*)(void *, const char *));
#m64p_error ConfigListSections(void *, void (*)(void *, const char *));
#
#typedef m64p_error (*ptr_ConfigOpenSection)(const char *, m64p_handle *);
#m64p_error ConfigOpenSection(const char *, m64p_handle *);
#
#typedef m64p_error (*ptr_ConfigListParameters)(m64p_handle, void *, void (*)(void *, const char *, m64p_type));
#m64p_error ConfigListParameters(m64p_handle, void *, void (*)(void *, const char *, m64p_type));
#
#typedef m64p_error (*ptr_ConfigSaveFile)(void);
#m64p_error ConfigSaveFile(void);
#
#typedef m64p_error (*ptr_ConfigSaveSection)(const char *);
#m64p_error ConfigSaveSection(const char *);
#
#typedef int (*ptr_ConfigHasUnsavedChanges)(const char *);
#int ConfigHasUnsavedChanges(const char *);
#
#typedef m64p_error (*ptr_ConfigDeleteSection)(const char *SectionName);
#m64p_error ConfigDeleteSection(const char *SectionName);
#
#typedef m64p_error (*ptr_ConfigRevertChanges)(const char *SectionName);
#m64p_error ConfigRevertChanges(const char *SectionName);
#
#typedef m64p_error (*ptr_ConfigSetParameter)(m64p_handle, const char *, m64p_type, const void *);
#m64p_error ConfigSetParameter(m64p_handle, const char *, m64p_type, const void *);
#
#typedef m64p_error (*ptr_ConfigSetParameterHelp)(m64p_handle, const char *, const char *);
#m64p_error ConfigSetParameterHelp(m64p_handle, const char *, const char *);
#
#typedef m64p_error (*ptr_ConfigGetParameter)(m64p_handle, const char *, m64p_type, void *, int);
#m64p_error ConfigGetParameter(m64p_handle, const char *, m64p_type, void *, int);
#
#typedef m64p_error (*ptr_ConfigGetParameterType)(m64p_handle, const char *, m64p_type *);
#m64p_error ConfigGetParameterType(m64p_handle, const char *, m64p_type *);
#
#typedef const char * (*ptr_ConfigGetParameterHelp)(m64p_handle, const char *);
#const char * ConfigGetParameterHelp(m64p_handle, const char *);
#
#typedef m64p_error (*ptr_ConfigSetDefaultInt)(m64p_handle, const char *, int, const char *);
#typedef m64p_error (*ptr_ConfigSetDefaultFloat)(m64p_handle, const char *, float, const char *);
#typedef m64p_error (*ptr_ConfigSetDefaultBool)(m64p_handle, const char *, int, const char *);
#typedef m64p_error (*ptr_ConfigSetDefaultString)(m64p_handle, const char *, const char *, const char *);
#
#m64p_error ConfigSetDefaultInt(m64p_handle, const char *, int, const char *);
#m64p_error ConfigSetDefaultFloat(m64p_handle, const char *, float, const char *);
#m64p_error ConfigSetDefaultBool(m64p_handle, const char *, int, const char *);
#m64p_error ConfigSetDefaultString(m64p_handle, const char *, const char *, const char *);
#typedef int (*ptr_ConfigGetParamInt)(m64p_handle, const char *);
#typedef float (*ptr_ConfigGetParamFloat)(m64p_handle, const char *);
#typedef int (*ptr_ConfigGetParamBool)(m64p_handle, const char *);
#typedef const char * (*ptr_ConfigGetParamString)(m64p_handle, const char *);
#
#int ConfigGetParamInt(m64p_handle, const char *);
#float ConfigGetParamFloat(m64p_handle, const char *);
#int ConfigGetParamBool(m64p_handle, const char *);
#const char * ConfigGetParamString(m64p_handle, const char *);
#typedef const char * (*ptr_ConfigGetSharedDataFilepath)(const char *);
#
#const char * ConfigGetSharedDataFilepath(const char *);
#typedef const char * (*ptr_ConfigGetUserConfigPath)(void);
#
#const char * ConfigGetUserConfigPath(void);
#typedef const char * (*ptr_ConfigGetUserDataPath)(void);
#
#const char * ConfigGetUserDataPath(void);
#typedef const char * (*ptr_ConfigGetUserCachePath)(void);
#
#const char * ConfigGetUserCachePath(void);
#
#typedef m64p_error (*ptr_ConfigExternalOpen)(const char *, m64p_handle *);
#m64p_error ConfigExternalOpen(const char *, m64p_handle *);
#
#typedef m64p_error (*ptr_ConfigExternalClose)(m64p_handle);
#m64p_error ConfigExternalClose(m64p_handle);
#
#typedef m64p_error (*ptr_ConfigExternalGetParameter)(m64p_handle, const char *, const char *, char *, int);
#
#m64p_error ConfigExternalGetParameter(m64p_handle, const char *, const char *, char *, int);
#typedef void (*ptr_DebugCallback)(void *Context, int level, const char *message);
#typedef void (*ptr_StateCallback)(void *Context, m64p_core_param param_type, int new_value);
#
#void DebugCallback(void *Context, int level, const char *message);
#void StateCallback(void *Context, m64p_core_param param_type, int new_value);
#
#typedef m64p_error (*ptr_CoreStartup)(int, const char *, const char *, void *, ptr_DebugCallback, void *, ptr_StateCallback);
#
#m64p_error CoreStartup(int, const char *, const char *, void *, ptr_DebugCallback, void *, ptr_StateCallback);
#
#typedef m64p_error (*ptr_CoreShutdown)(void);
#m64p_error CoreShutdown(void);
#
#typedef m64p_error (*ptr_CoreAttachPlugin)(m64p_plugin_type, m64p_dynlib_handle);
#m64p_error CoreAttachPlugin(m64p_plugin_type, m64p_dynlib_handle);
#
#typedef m64p_error (*ptr_CoreDetachPlugin)(m64p_plugin_type);
#m64p_error CoreDetachPlugin(m64p_plugin_type);
#
#typedef m64p_error (*ptr_CoreDoCommand)(m64p_command, int, void *);
#m64p_error CoreDoCommand(m64p_command, int, void *);
#
#typedef m64p_error (*ptr_CoreOverrideVidExt)(m64p_video_extension_functions *);
#m64p_error CoreOverrideVidExt(m64p_video_extension_functions *);
#
#typedef m64p_error (*ptr_CoreAddCheat)(const char *, m64p_cheat_code *, int);
#m64p_error CoreAddCheat(const char *, m64p_cheat_code *, int);
#
#typedef m64p_error (*ptr_CoreCheatEnabled)(const char *, int);
#m64p_error CoreCheatEnabled(const char *, int);
#
#typedef m64p_error (*ptr_CoreGetRomSettings)(m64p_rom_settings *, int, int, int);
#m64p_error CoreGetRomSettings(m64p_rom_settings *, int, int, int);
