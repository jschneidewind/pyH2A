import numpy as np
from functools import lru_cache

from pyH2A.Utilities.input_modification import file_import
from pyH2A.Plugins.Plugin import Plugin
from pyH2A.DiscountedCashFlow import DiscountedCashFlow

class HourlyIrradiationPlugin(Plugin):
    '''Calculation of hourly and mean daily irradiation data with different module configurations.
    
    Parameters
    ----------
    Hourly Irradiation > File > Value : str
        Path to a `.csv` file containing hourly irradiance data as provided by
        https://re.jrc.ec.europa.eu/pvg_tools/en/#TMY, ``process_table()`` is used.
    Irradiance Area Parameters > Module Tilt (degrees) > Value : float
        Tilt of irradiated module in degrees.
    Irradiance Area Parameters > Array Azimuth (degrees) > Value : float
        Azimuth angle of irradiated module in degrees.
    Irradiance Area Parameters > Nominal Operating Temperature (Celsius) > Value : float
        Nominal operating temperature of irradiated module in degrees Celsius.
    Irradiance Area Parameters > Mismatch Derating > Value : float
        Derating value due to mismatch (percentage or value between 0 and 1).
    Irradiance Area Parameters > Dirt Derating > Value : float
        Derating value due to dirt buildup (percentage or value between 0 and 1).
    Irradiance Area Parameters > Temperature Coefficient (per Celsius) > Value : float
        Performance decrease of irradiated module per degree Celsius increase.
    
    Returns
    -------
    Hourly Irradiation > No Tracking (kW) > Value : ndarray
        Hourly irradiation with no tracking per m2 in kW.
    Hourly Irradiation > Horizontal Single Axis Tracking (kW) > Value : ndarray
        Hourly irradiation with single axis tracking per m2 in kW.
    Hourly Irradiation > Two Axis Tracking (kW) > Value : ndarray
        Hourly irradiation with two axis tracking per m2 in kW.
    Hourly Irradiation > Mean solar input (kWh/m2/day) > Value : float
        Mean solar input with no tracking in kWh/m2/day.
    Hourly Irradiation > Mean solar input, single axis tracking (kWh/m2/day) > Value : float
        Mean solar input with single axis tracking in kWh/m2/day.
    Hourly Irradiation > Mean solar input, two axis tracking (kWh/m2/day) > Value : float
        Mean solar input with two axis tracking in kWh/m2/day.
    '''

    def __init__(
            self, 
            dcf: DiscountedCashFlow
            ) -> None:
        super().__init__(dcf)

        # Process the "Hourly Irradiation" table
        table_keys = ['Hourly Irradiation']
        self.process_table(table_keys)

        data, location = import_hourly_data(dcf.inp['Hourly Irradiation']['File']['Value'])
        
        # Insert location data using dictionary entries
        self.insert_queue.extend([
            {'key': 'Hourly Irradiation', 'subkey': 'Latitude', 'value': location['Latitude (decimal degrees)']},
            {'key': 'Hourly Irradiation', 'subkey': 'Longitude', 'value': location['Longitude (decimal degrees)']}
        ])
        self.process_insert_queue()
        
        # Process the "Irradiance Area Parameters" table
        table_keys = ['Irradiance Area Parameters']
        self.process_table(table_keys)

        pv = self.dcf.inp['Irradiance Area Parameters']

        self.power_kW, self.power_sat_kW, self.power_dat_kW = calculate_PV_power_ratio(
            self.dcf.inp['Hourly Irradiation']['File']['Value'],
            pv['Module Tilt (degrees)']['Value'], 
            pv['Array Azimuth (degrees)']['Value'],
            pv['Nominal Operating Temperature (Celsius)']['Value'], 
            pv['Temperature Coefficient (per Celsius)']['Value'],
            pv['Mismatch Derating']['Value'], 
            pv['Dirt Derating']['Value']
        )

        # Insert calculated irradiation data
        self.insert_queue.extend([
            {'key': 'Hourly Irradiation', 'subkey': 'No Tracking (kW)', 'value': self.power_kW},
            {'key': 'Hourly Irradiation', 'subkey': 'Horizontal Single Axis Tracking (kW)', 'value': self.power_sat_kW},
            {'key': 'Hourly Irradiation', 'subkey': 'Two Axis Tracking (kW)', 'value': self.power_dat_kW},
            {'key': 'Hourly Irradiation', 'subkey': 'Mean solar input no tracking (kWh/m2/day)', 'value': np.sum(self.power_kW) / 365.},
            {'key': 'Hourly Irradiation', 'subkey': 'Mean solar input single axis tracking (kWh/m2/day)', 'value': np.sum(self.power_sat_kW) / 365.},
            {'key': 'Hourly Irradiation', 'subkey': 'Mean solar input two axis tracking (kWh/m2/day)', 'value': np.sum(self.power_dat_kW) / 365.}
        ])
        self.process_insert_queue()

@lru_cache(maxsize=None)
def import_hourly_data(
        file_name: str
        ) -> tuple[dict, dict]:
    '''Imports hourly irradiation data and location coordinates from the `.csv` format provided 
    by: https://re.jrc.ec.europa.eu/pvg_tools/en/#TMY.
    ``@lru_cache`` is used for fast repeated reads.
    '''
    with file_import(file_name, mode='r') as f:
        data = np.genfromtxt(f, delimiter=',', skip_header=17, skip_footer=9, converters={0: converter_function})

    strings = ['Latitude (decimal degrees)', 'Longitude (decimal degrees)']
    location = {}

    file_read = file_import(file_name, mode='r')
    for line in file_read:
        split = line.split(':')
        if split[0] in strings:
            location[split[0]] = float(split[1].strip(' '))
        else:
            break
    file_read.close()

    data_dict = {
        'Time': data[:, 0],
        'Temperature': data[:, 1],
        'Global Horizontal Irradiance': data[:, 3],
        'Direct Normal Irradiance': data[:, 4],
        'Diffuse Horizontal Irradiance': data[:, 5]
    }

    return data_dict, location

def converter_function(
        string: str
        ) -> float:
    '''Converter function for datetime of hourly irradiation data.'''
    split = str(string).split(':')
    return float(split[1][:2])

@lru_cache(maxsize=None)
def calculate_PV_power_ratio(
        file_name: str, 
        module_tilt: float, 
        array_azimuth: float, 
        nominal_operating_temperature: float,
        temperature_coefficient: float, 
        mismatch_derating: float, 
        dirt_derating: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    '''Calculation based on Chang 2020, https://doi.org/10.1016/j.xcrp.2020.100209
    SAT: horizontal single axis tracking
    DAT: dual axis tracking, no diffuse radiation
    '''
    data, location = import_hourly_data(file_name)
    latitude = location['Latitude (decimal degrees)']
    longitude = location['Longitude (decimal degrees)']

    day_number = np.arange(1, len(data['Time']) + 1) / 24
    declination_angle = 23.45 * np.sin((day_number - 81) * 2 * np.pi / 365.)
    hour_angle = (data['Time'] - 12) * 15 + longitude

    altitude_angle = 360 / (2 * np.pi) * np.arcsin(
        np.sin(2 * np.pi / 360 * declination_angle) * np.sin(2 * np.pi / 360 * latitude) +
        np.cos(2 * np.pi / 360 * declination_angle) * np.cos(2 * np.pi / 360 * latitude) * np.cos(2 * np.pi / 360 * hour_angle)
    )

    azimuth_angle = 360 / (2 * np.pi) * np.arccos(
        (np.sin(2 * np.pi / 360 * declination_angle) * np.cos(2 * np.pi / 360 * latitude) -
         np.cos(2 * np.pi / 360 * declination_angle) * np.sin(2 * np.pi / 360 * latitude) *
         np.cos(2 * np.pi / 360 * hour_angle)) /
        np.cos(2 * np.pi / 360 * altitude_angle)
    ) * np.sign(hour_angle)

    dni_fraction = (
        np.cos(2 * np.pi / 360 * altitude_angle) * np.sin(2 * np.pi / 360 * module_tilt) *
        np.cos(2 * np.pi / 360 * (array_azimuth - azimuth_angle)) +
        np.sin(2 * np.pi / 360 * altitude_angle) * np.cos(2 * np.pi / 360 * module_tilt)
    )
    dni_fraction = dni_fraction.clip(min=0)

    direct_plane_radiation = data['Direct Normal Irradiance'] * dni_fraction
    diffuse_plane_radiation = data['Diffuse Horizontal Irradiance'] * (180 - module_tilt) / 180
    total_plane_radiation = direct_plane_radiation + diffuse_plane_radiation

    cell_temperature = data['Temperature'] + (nominal_operating_temperature - 20) * total_plane_radiation / 800
    temperature_derating = 1 + temperature_coefficient * (cell_temperature - 25)

    power_kW = (temperature_derating * mismatch_derating * dirt_derating * total_plane_radiation / 1000)

    sat_azimuth = np.sign(azimuth_angle) * 90
    sat_tilt = 360 / (2 * np.pi) * np.arctan(
        1 / np.tan(2 * np.pi / 360 * altitude_angle) * np.cos(2 * np.pi / 360 * (sat_azimuth - azimuth_angle))
    )
    sat_fraction = (
        np.cos(2 * np.pi / 360 * altitude_angle) * np.sin(2 * np.pi / 360 * sat_tilt) *
        np.cos(2 * np.pi / 360 * (sat_azimuth - azimuth_angle)) +
        np.sin(2 * np.pi / 360 * altitude_angle) * np.cos(2 * np.pi / 360 * sat_tilt)
    )
    sat_fraction = sat_fraction.clip(min=0)

    sat_direct_POA = sat_fraction * data['Direct Normal Irradiance']
    sat_diffuse_POA = data['Diffuse Horizontal Irradiance'] * (180 - sat_tilt) / 180
    sat_total_POA = sat_direct_POA + sat_diffuse_POA

    power_sat_kW = (temperature_derating * mismatch_derating * dirt_derating * sat_total_POA / 1000)
    power_dat_kW = (data['Direct Normal Irradiance'] * temperature_derating * mismatch_derating * dirt_derating / 1000)

    return power_kW, power_sat_kW, power_dat_kW
