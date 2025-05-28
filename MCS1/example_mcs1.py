from smaract_mcs1 import SmarActMCS

mcs = SmarActMCS("dll/MCSControl.dll")
print("Opening MCS system...")
mcs.open()
print("Number of channels:", mcs.get_num_channels())
channel = 1
steps = -2000
amplitude = 4095
frequency = 2000
print(f"Moving channel {channel} {steps} steps with amplitude {amplitude} and frequency {frequency}")
mcs.step_move(channel, steps, amplitude, frequency)
print("Move completed.")
mcs.close()
print("MCS system closed.")
