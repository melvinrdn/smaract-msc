from smaract_mcs1 import SmarActMCS

mcs = SmarActMCS("dll/MCSControl.dll")
mcs.open()
print("Number of channels:", mcs.get_num_channels())
mcs.move_relative(0, 1000)
mcs.close()
