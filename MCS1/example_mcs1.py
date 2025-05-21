from smaract_mcs1 import SmarActMCS

mcs = SmarActMCS("dll/MCSControl.dll")
mcs.open()
print("Number of channels:", mcs.get_num_channels())
mcs.step_move(0,10000)
mcs.close()
