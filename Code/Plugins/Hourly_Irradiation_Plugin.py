from input_modification import insert, process_table, read_textfile
import numpy as np
from functools import lru_cache
from timeit import default_timer as timer
import matplotlib.pyplot as plt

class Hourly_Irradiation_Plugin:
	'''
	______________
	Required Input
	______________
	
	# Hourly Irradiation
	Name | Value
	--- | ---
	File | str

	process_table() is used. str should be a path to file containing a .csv file with hourly irradiance data
	as provided by https://re.jrc.ec.europa.eu/pvg_tools/en/#TMY

	# Irradiance Area Parameters
	Name | Value
	--- | ---
	Module Tilt (degrees) | num
	Array Azimuth (degrees) | num
	Nominal Operating Temperature (Celcius) | num
	Mismatch Derating | num
	Dirt Derating | num
	Temperature Coefficienct (per Celcius) | num

	process_table() is used.

	______________
	Output
	______________
		
	Hourly Irradiation > No Tracking (kW) > Value
	Hourly Irradiation > Horizontal Single Axis Tracking (kW) > Value
	Hourly Irradiation > Two Axis Tracking (kW) > Value
	Hourly Irradiation > Mean solar input (kWh/m2/day) > Value
	Hourly Irradiation > Mean solar input, single axis tracking (kWh/m2/day) > Value
	Hourly Irradiation > Mean solar input, two axis tracking (kWh/m2/day) > Value
	'''

	def __init__(hour, self, print_info):
		process_table(self.inp, 'Hourly Irradiation', 'Value')

		data, location = import_hourly_data(self.inp['Hourly Irradiation']['File']['Value'])

		insert(self, 'Hourly Irradiation', 'Latitude', 'Value', location['Latitude (decimal degrees)'], __name__, print_info = print_info)
		insert(self, 'Hourly Irradiation', 'Longitude', 'Value', location['Longitude (decimal degrees)'], __name__, print_info = print_info)

		process_table(self.inp, 'Irradiance Area Parameters', 'Value')

		pv = self.inp['Irradiance Area Parameters']

		hour.power_kW, hour.power_sat_kW, hour.power_dat_kW = calculate_PV_power_ratio(self.inp['Hourly Irradiation']['File']['Value'],
											pv['Module Tilt (degrees)']['Value'], pv['Array Azimuth (degrees)']['Value'],
											pv['Nominal Operating Temperature (Celcius)']['Value'], 
											pv['Temperature Coefficienct (per Celcius)']['Value'],
											pv['Mismatch Derating']['Value'], pv['Dirt Derating']['Value'])

		insert(self, 'Hourly Irradiation', 'No Tracking (kW)', 'Value', hour.power_kW, __name__, print_info = print_info)
		insert(self, 'Hourly Irradiation', 'Horizontal Single Axis Tracking (kW)', 'Value', hour.power_sat_kW, __name__, print_info = print_info)
		insert(self, 'Hourly Irradiation', 'Two Axis Tracking (kW)', 'Value', hour.power_dat_kW, __name__, print_info = print_info)

		insert(self, 'Hourly Irradiation', 'Mean solar input no tracking (kWh/m2/day)', 'Value', np.sum(hour.power_kW)/365., __name__, print_info = print_info)
		insert(self, 'Hourly Irradiation', 'Mean solar input single axis tracking (kWh/m2/day)', 'Value', np.sum(hour.power_sat_kW)/365., __name__, print_info = print_info)
		insert(self, 'Hourly Irradiation', 'Mean solar input two axis tracking (kWh/m2/day)', 'Value', np.sum(hour.power_dat_kW)/365., __name__, print_info = print_info)

def converter_function(string):
	'''Converter function for datetime of hourly irradiation data'''

	decoded = string.decode('utf-8')
	split = decoded.split(':')

	return float(split[1][:2]) #- 0.5

def import_Chang_data(file_name):

	file_name = '../Lookup_Tables/Hourly_Irradiation_Data_Townsville_Chang_2020.csv'

	data = read_textfile(file_name, delimiter = '	')

	data_dict = {'Time': data[:,0] - 10., 'Temperature': data[:,1],
				  'Direct Normal Irradiance': data[:,2], 'Diffuse Horizontal Irradiance': data[:,3]}

	location = {'Latitude (decimal degrees)': -19.25, 'Longitude (decimal degrees)': 146.77}

	return data_dict, location
	
@lru_cache(maxsize = None)
def import_hourly_data(file_name):
	'''
	Imports hourly irradiation data and location coordinates from the .csv format provided by: https://re.jrc.ec.europa.eu/pvg_tools/en/#TMY
	@lru_cache is used for fast repeated reads
	'''
	data = np.genfromtxt(file_name, delimiter = ',', skip_header = 17, skip_footer = 9, 
						 converters = {0: converter_function})
	
	strings = ['Latitude (decimal degrees)', 'Longitude (decimal degrees)']
	location = {}

	with open(file_name, 'r') as file_read:
		for row_counter, line in enumerate(file_read):

			split = line.split(':')

			if split[0] in strings:
				location[split[0]] = float(split[1].strip(' '))
			else:
				break

	data_dict = {'Time': data[:,0], 'Temperature': data[:,1], 'Global Horizontal Irradiance':  data[:,3],
				  'Direct Normal Irradiance': data[:,4], 'Diffuse Horizontal Irradiance': data[:,5]}

	return data_dict, location

@lru_cache(maxsize = None)
def calculate_PV_power_ratio(file_name, module_tilt, array_azimuth, nominal_operating_temperature,
							 temperature_coefficient, mismatch_derating, dirt_derating):
	'''
	Calculation based on Chang 2020, https://doi.org/10.1016/j.xcrp.2020.100209
	SAT: horzontal single axis tracking
	DAT: dual axis tracking, no diffuse radiation
	'''

	data, location = import_hourly_data(file_name)
	#data, location = import_Chang_data(file_name)

	latitude = location['Latitude (decimal degrees)']
	longitude = location['Longitude (decimal degrees)']

	day_number = np.arange(1, len(data['Time']) + 1) / 24
	#day_number = np.arange(0, len(data['Time'])) / 24

	declination_angle = 23.45 * np.sin((day_number - 81) * 2 * np.pi / 365.)
	hour_angle = (data['Time'] - 12) * 15 + longitude

	altitude_angle = 360 / (2 * np.pi) * np.arcsin(np.sin(2 * np.pi / 360 * declination_angle) * 
					 np.sin(2 * np.pi / 360 * latitude) + np.cos(2 * np.pi / 360 * declination_angle) * 
					 np.cos(2 * np.pi / 360 * latitude) * np.cos(2 * np.pi / 360 * hour_angle))

	azimuth_angle = 360 / (2 * np.pi) * np.arccos((np.sin(2 * np.pi / 360 * declination_angle) * 
					np.cos(2 * np.pi / 360 * latitude) - np.cos( 2 * np.pi / 360 * declination_angle) * 
					np.sin(2 * np.pi / 360 * latitude) * np.cos(2 * np.pi / 360 * hour_angle)) / 
					np.cos(2 * np.pi / 360 * altitude_angle)) * np.sign(hour_angle)

	dni_fraction = np.cos(2 * np.pi / 360 * altitude_angle) * np.sin(2 * np.pi / 360 * 
				   module_tilt) * np.cos(2 * np.pi / 360 * (array_azimuth - 
				   azimuth_angle)) + np.sin(2 * np.pi / 360 * altitude_angle) * np.cos(2 * np.pi / 
				   360 * module_tilt)
	dni_fraction = dni_fraction.clip(min = 0)

	direct_plane_radiation = data['Direct Normal Irradiance'] * dni_fraction
	diffuse_plane_radiation = data['Diffuse Horizontal Irradiance'] * (180 - module_tilt) / 180
	total_plane_radiation = direct_plane_radiation + diffuse_plane_radiation

	cell_temperature = data['Temperature'] + (nominal_operating_temperature - 
					   20) * total_plane_radiation/800  #where does this formula come from?

	temperature_derating = 1 + temperature_coefficient * (cell_temperature - 25)  # why the 25 correction?

	power_kW = (temperature_derating * mismatch_derating * 
					 dirt_derating * total_plane_radiation/1000)  # Converting W to kW

	sat_azimuth = np.sign(azimuth_angle) * 90

	sat_tilt = 360 / (2 * np.pi) * np.arctan(1 / np.tan(2 * np.pi / 360 * altitude_angle) * 
			   np.cos( 2 * np.pi / 360 * (sat_azimuth - azimuth_angle)))

	sat_fraction = (np.cos(2 * np.pi / 360 * altitude_angle) * np.sin(2 * np.pi / 360 * sat_tilt) * 
					np.cos(2 * np.pi / 360 * (sat_azimuth - azimuth_angle)) + np.sin(2 * np.pi / 360 * altitude_angle) * 
					np.cos(2 * np.pi / 360 * sat_tilt))
	sat_fraction = sat_fraction.clip(min = 0)

	sat_direct_POA = sat_fraction * data['Direct Normal Irradiance']
	sat_diffuse_POA = data['Diffuse Horizontal Irradiance'] * (180 - sat_tilt) / 180
	sat_total_POA = sat_direct_POA + sat_diffuse_POA

	power_sat_kW = (temperature_derating * mismatch_derating * 
					 dirt_derating * sat_total_POA / 1000)  # Convert W to kW

	power_dat_kW = (data['Direct Normal Irradiance'] * temperature_derating * 
					mismatch_derating * dirt_derating / 1000)

	return power_kW, power_sat_kW, power_dat_kW

