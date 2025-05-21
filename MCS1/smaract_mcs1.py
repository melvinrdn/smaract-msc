import ctypes
import time
from ctypes import c_uint, c_char_p, byref, create_string_buffer

SA_OK = 0
SA_TARGET_STATUS = 4  # status bit for active target movement

class SmarActMCS:
    """
    Python wrapper for SmarAct MCS Control using MCSControl.dll (synchronous mode).
    """

    def __init__(self, dll_path: str):
        self.lib = ctypes.windll.LoadLibrary(dll_path)
        self.system_index = c_uint(0)

    def open(self):
        """
        Automatically discovers and opens the first available MCS system.
        """
        # Discover available systems
        buffer = create_string_buffer(1024)
        size = c_uint(1024)
        res = self.lib.SA_FindSystems(None, buffer, byref(size))
        if res != SA_OK:
            raise RuntimeError(f"SA_FindSystems failed with code {res}")
        
        locator = buffer.value.decode()
        if not locator:
            raise RuntimeError("No MCS system found.")

        # Open the system in synchronous mode
        res = self.lib.SA_OpenSystem(byref(self.system_index), c_char_p(locator.encode()), c_char_p(b"sync"))
        if res != SA_OK:
            raise RuntimeError(f"SA_OpenSystem failed with code {res}")

    def close(self):
        """Closes the MCS system."""
        self.lib.SA_CloseSystem(self.system_index)

    def step_move(self, channel: int, steps: int, amplitude: int = 4095, frequency: int = 2000):
        """
        Performs a step mov.

        Parameters
        ----------
        channel : int
            Channel index
        steps : int
            Number of steps
        amplitude : int
            Step amplitude
        frequency : int
            Step frequency
        """
        res = self.lib.SA_StepMove_S(self.system_index, channel, steps, amplitude, frequency)
        if res != SA_OK:
            raise RuntimeError(f"SA_StepMove_S failed with code {res}")
        self._wait_until_done(channel)

    def get_num_channels(self) -> int:
        """Returns number of available channels."""
        count = c_uint()
        res = self.lib.SA_GetNumberOfChannels(self.system_index, byref(count))
        if res != SA_OK:
            raise RuntimeError(f"SA_GetNumberOfChannels failed with code {res}")
        return count.value

    def _wait_until_done(self, channel: int):
        """
        Internal: Waits until a move or command finishes on a given channel.
        """
        status = c_uint()
        while True:
            self.lib.SA_GetStatus_S(self.system_index, channel, byref(status))
            if status.value != SA_TARGET_STATUS:
                break
            time.sleep(0.05)
