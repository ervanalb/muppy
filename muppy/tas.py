import logging
import struct
from muppy import InputPlugin, ControllerInfo, Core, Plugin, PluginType, CoreParam, EmuState
from typing import List, Optional, Any

logger = logging.getLogger(__name__)

class TASPlayerError(Exception):
    pass

class TASPlayer(InputPlugin):
    plugin_name = "TAS Player Input Plugin"

    def __init__(self, core: Core, filename: str, backup_plugin: Optional[Any]=None):
        super().__init__(core)

        self.backup_plugin = None
        if backup_plugin:
            self.backup_plugin = Plugin.make(self.core, backup_plugin)
            if self.backup_plugin.version.plugin_type != PluginType.INPUT:
                raise ValueError("Backup plugin is not an input plugin")

        self.file = open(filename, "rb")

        header_fmt = "<4sIiIIBB2xIH2xI160x32sIH56x64s64s64s64s222s256s"
        header = self.file.read(0x400)
        if len(header) < 0x400:
            raise TASPlayerError("Not a .m64 file")

        (
            signature,
            version,
            movie_uid,
            frame_count,
            rerecord_count,
            fps,
            controller_count,
            sample_count,
            movie_start_type,
            controller_flags,
            rom_name,
            rom_crc32,
            rom_country,
            video_plugin,
            sound_plugin,
            input_plugin,
            rsp_plugin,
            author,
            description
        ) = struct.unpack(header_fmt, header)

        if signature != b"M64\x1A":
            raise TASPlayerError("Not a .m64 file")
        if version != 3:
            raise TASPlayerError("Only version 3 is supported (got {})".format(version))
        if movie_start_type != 2:
            raise TASPlayerError("Only movies starting from power-on are supported")
        self.connected_controllers = [bool(controller_flags & (1 << (i * 4))) for i in range(4)]

        rom_name = str(rom_name, encoding="latin1")
        video_plugin = str(video_plugin, encoding="latin1")
        sound_plugin = str(sound_plugin, encoding="latin1")
        input_plugin = str(input_plugin, encoding="latin1")
        rsp_plugin = str(rsp_plugin, encoding="latin1")
        author = str(author, encoding="utf8")
        description = str(description, encoding="utf8")

        logger.info("File: {}".format(filename))
        logger.info("For ROM: {}".format(rom_name))
        logger.info("Frames: {}".format(frame_count))
        logger.info("Author: {}".format(author))
        logger.info("Description: {}".format(description))

        self.skip = 1 # skip first get_keys call

    def get_keys(self, controller: int) -> (int, int, int):
        no_input = (0, 0, 0)
        if self.skip:
            self.skip -= 1
            return no_input

        if not self.connected_controllers[controller]:
            return no_input

        if self.file.closed:
            return no_input

        inputs = self.file.read(4)
        if len(inputs) < 4:
            logger.info("Reached end of input")
            self.file.close()
            self.attach_backup_plugin()
            return no_input

        inputs = struct.unpack("<Hbb", inputs)
        return inputs

    def attach_backup_plugin(self):
        if not self.backup_plugin:
            return

        def _cb(param_type, new_value):
            if param_type == CoreParam.STATE_SAVECOMPLETE:
                self.core.stop()
            elif param_type == CoreParam.EMU_STATE and new_value == EmuState.STOPPED:
                self.core.attach_plugin(self.backup_plugin)
                self.core.execute()
            elif param_type == CoreParam.EMU_STATE and new_value == EmuState.RUNNING:
                self.core.remove_state_callback(_cb)
                self.core.state_load(self.ss)
        self.core.add_state_callback(_cb)
        self.ss = self.core.state_save()

    def initiate_controllers(self) -> List[ControllerInfo]:
        return [ControllerInfo(present=p, raw_data=False, plugin=False) for p in self.connected_controllers]
