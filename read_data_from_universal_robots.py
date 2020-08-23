#Requires UR-Robot with at least CB3.4
#works with all robots (CB or e-series)
# inspired by https://www.universal-robots.com/articles/ur/real-time-data-exchange-rtde-guide/
import sys
import time
import datetime
import logging
import rtde as rtde
import rtde_config as rtde_config
import socket

#Initial Values
datarate=10 # Time interval for data logging in Hz


#######################################################

ROBOT_HOST = '192.168.1.103'
ROBOT_PORT = 30004
config_filename = 'control_loop_configuration.xml'



keep_running = True
#Initialize RTDE Connection
logging.getLogger().setLevel(logging.INFO)
conf = rtde_config.ConfigFile(config_filename)
state_names, state_types = conf.get_recipe('state')
watchdog_names, watchdog_types = conf.get_recipe('watchdog')
con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
con.connect()
connected = con.is_connected()
if connected == True:
	print('Connected')

# get controller version
con.get_controller_version()

# setup recipes
con.send_output_setup(state_names, state_types)
watchdog = con.send_input_setup(watchdog_names, watchdog_types)

sensor_data = {}
# The function "rtde_set_watchdog" in the "rtde_control_loop.urp" creates a 1 Hz watchdog
watchdog.input_int_register_0 = 0
##########################################################################
#FUNCTIONS
def Dashboard(string): #Send a command to the Dashboard Server of the Robot
	Message=string+'\n'
	s = socket.socket()
	s.connect((ROBOT_HOST, Dashboard_PORT))
	s.send(Message)
	return
def read_data(sensor_data):
	sensor_data['Time'] = round(t1-t0,4)
	sensor_data['Force'] = round(state.tcp_force_scalar,4)
	sensor_data['TCP_X'] = round(state.actual_TCP_pose[0],4)
	sensor_data['TCP_Y'] = round(state.actual_TCP_pose[1],4)
	sensor_data['TCP_Z'] = round(state.actual_TCP_pose[2],4)
	sensor_data['TCP_RX'] = round(1/np.pi*180*state.actual_TCP_pose[3],4)
	sensor_data['TCP_RY'] = round(1/np.pi*180*state.actual_TCP_pose[4],4)
	sensor_data['TCP_RZ'] = round(1/np.pi*180*state.actual_TCP_pose[5],4)
	sensor_data['Joint1'] = round(1/np.pi*180*state.actual_q[0],4)
	sensor_data['Joint2'] = round(1/np.pi*180*state.actual_q[1],4)
	sensor_data['Joint3'] = round(1/np.pi*180*state.actual_q[2],4)
	sensor_data['Joint4'] = round(1/np.pi*180*state.actual_q[3],4)
	sensor_data['Joint5'] = round(1/np.pi*180*state.actual_q[4],4)
	sensor_data['Joint6'] = round(1/np.pi*180*state.actual_q[5],4)
	return sensor_data

##########################################################################
#start data synchronization
if not con.send_start():
    sys.exit()

##########################################################################
t0=time.clock() #time stamp
t0_temp=time.clock() #temporary time stamp

print('Reading from robot')

try:
	while keep_running:
		# receive the current state
		# the data that will be received is configured in the
		# control_loop_configuration.xml
		state = con.receive()
		t1=time.clock()
		if t1-t0_temp>=1./datarate:
			sensor_data = read_data(sensor_data) #put data from state in a dictionary
			print(sensor_data)
			# or do something else with the dictionary...

			t0_temp=time.clock()
		con.send(watchdog) # kick watchdog
except KeyboardInterrupt:
	con.send_pause() #RTDE
	con.disconnect() #RTDE
