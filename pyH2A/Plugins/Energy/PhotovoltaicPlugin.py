from pyH2A.DiscountedCashFlow import DiscountedCashFlow
from pyH2A.Utilities.input_modification import read_textfile, hourly_to_daily_power
from pyH2A.Plugins.Plugin import Plugin
import numpy as np


class PhotovoltaicPlugin(Plugin):
    '''Simulation of electricity production using PV.

    Parameters
    ----------
    Irradiation Used > Data > Value : str or ndarray
        Hourly power ratio data for electricity production calculation. Either a 
        path to a text file containing the data or ndarray. A suitable array 
        can be retrieved from "Hourly Irradiation > *type of tracking* > Value".
    CAPEX Multiplier > Multiplier > Value : float
        Multiplier to describe cost reduction of PV CAPEX for every ten-fold
        increase of power relative to CAPEX reference power. Based on the multiplier the CAPEX
        scaling factor is calculated as: multiplier ^ (number of ten-fold increases). A value
        of 1 leads to no CAPEX reduction, a value < 1 enables cost reduction.
    Photovoltaic > Nominal Power (kW) > Value : float
        Nominal power of PV array in kW.
    Photovoltaic > CAPEX Reference Power (kW) > Value : float
        Reference power of PV array for cost reduction calculations.
    Photovoltaic > Power loss per year > Value : float
        Reduction in power produced by PV array per year due to degradation. Percentage or value
        > 0. Reduction calculated as: (1 - loss per year) ^ year.
    Photovoltaic > Efficiency > Value : float
        Power conversion efficiency of used solar cells. Percentage or value between 0 and 1.

    Returns
    -------
    Photovoltaic > Scaling Factor > Value : float
        CAPEX scaling factor for PV array calculated based on CAPEX multiplier, 
        reference and nominal power.
    Power Generation > PV Hourly Power Generation (kWh) > Value : dict
        Hourly power generation of PV array in kWh (dictionary of years).
    Power Generation > Available Power (hourly, kWh) > Value : dict
        Available power, hourly basis, dictionary of years (in kWh).
    Power Generation > Available Power (daily, kWh) > Value : dict
        Available power, daily basis, dictionary of years (in kWh).
    Non-Depreciable Capital Costs > Land required (acres) > Value : float
        Total land required in acres.
    Non-Depreciable Capital Costs > Solar Collection Area (m2) > Value : float
        Solar collection area in m2.
    LCA - Exports > PV Nominal Power > Value : float
        Nominal power of PV array in kW.
    '''

    def __init__(
            self, 
            dcf: DiscountedCashFlow
            ) -> None:
        super().__init__(dcf)

        table_keys: list = ['Irradiation Used', 'CAPEX Multiplier', 'Photovoltaic']
        self.process_table(table_keys)
        self.run_plugin()
        self.process_insert_queue()

    def run_plugin(
            self
            ) -> None:
        '''Run the Photovoltaic plugin.'''
        tea = PhotovoltaicPluginTEA(self)
        lca = PhotovoltaicPluginLCA(self)

        tea.calculate_power_production()
        tea.calculate_scaling_factors()
        tea.calculate_area()
        lca.export_nominal_power()


class PhotovoltaicPluginTEA:
    '''Handles techno-economic analysis calculations for the photovoltaic plugin.'''
    def __init__(
            self, 
            plugin: PhotovoltaicPlugin
            ) -> None:
        self.plugin: PhotovoltaicPlugin = plugin

    def calculate_power_production(
            self
            ) -> None:
        '''Using hourly irradiation data and PV array parameters,
        power production is calculated.
        '''
        # Determine if the data is a path or an ndarray
        if isinstance(self.plugin.dcf.inp['Irradiation Used']['Data']['Value'], str):
            data: np.ndarray = read_textfile(
                self.plugin.dcf.inp['Irradiation Used']['Data']['Value'], delimiter='	'
            )[:, 1]
        else:
            data: np.ndarray = self.plugin.dcf.inp['Irradiation Used']['Data']['Value']

        yearly_data: dict = {}
        yearly_data_daily_power: dict = {}

        for year in self.plugin.dcf.operation_years:
            data_loss_corrected: np.ndarray = self.calculate_photovoltaic_loss_correction(data, year)
            power_generation: np.ndarray = data_loss_corrected * self.plugin.dcf.inp['Photovoltaic']['Nominal Power (kW)']['Value']

            yearly_data[year] = power_generation
            yearly_data_daily_power[year] = hourly_to_daily_power(power_generation)
        
        self.plugin.yearly_power_generation = yearly_data
        self.plugin.insert_queue.extend([
            {'key': 'Power Generation', 'subkey': 'PV Hourly Power Generation (kWh)', 'value': yearly_data},
            {'key': 'Power Generation', 'subkey': 'Available Power (hourly, kWh)', 'value': yearly_data},
            {'key': 'Power Generation', 'subkey': 'Available Power (daily, kWh)', 'value': yearly_data_daily_power}
        ])

    def calculate_photovoltaic_loss_correction(
            self, 
            data: np.ndarray, 
            year: int
            ) -> np.ndarray:
        '''Calculation of yearly reduction in electricity production by PV array.'''
        return data * (1. - self.plugin.dcf.inp['Photovoltaic']['Power loss per year']['Value']) ** year

    def calculate_scaling_factors(
            self
            ) -> None:
        '''Calculation of PV CAPEX scaling factors.'''
        pv_scaling_factor: float = self.scaling_factor(
            self.plugin.dcf.inp['Photovoltaic']['Nominal Power (kW)']['Value'], 
            self.plugin.dcf.inp['Photovoltaic']['CAPEX Reference Power (kW)']['Value']
        )
        self.plugin.insert_queue.append(
            {'key': 'Photovoltaic', 'subkey': 'Scaling Factor', 'value': pv_scaling_factor}
        )

    def scaling_factor(
            self, 
            power: float, 
            reference: float
            ) -> float:
        '''Calculation of CAPEX scaling factor based on nominal and reference power.'''
        number_of_tenfold_increases: float = np.log10(power / reference)
        return self.plugin.dcf.inp['CAPEX Multiplier']['Multiplier']['Value'] ** number_of_tenfold_increases

    def calculate_area(
            self
            ) -> None:
        '''Area requirement calculation assuming 1000 W/m2 peak power.'''
        peak_kW_per_m2: float = self.plugin.dcf.inp['Photovoltaic']['Efficiency']['Value'] * 1.0
        area_m2: float = self.plugin.dcf.inp['Photovoltaic']['Nominal Power (kW)']['Value'] / peak_kW_per_m2
        area_acres: float = area_m2 * 0.000247105

        self.plugin.insert_queue.extend([
            {'key': 'Non-Depreciable Capital Costs', 'subkey': 'Land required (acres)', 'value': area_acres},
            {'key': 'Non-Depreciable Capital Costs', 'subkey': 'Solar Collection Area (m2)', 'value': area_m2}
        ])


class PhotovoltaicPluginLCA:
    '''Handles life-cycle assessment (LCA) calculations for the photovoltaic plugin.'''
    def __init__(
            self, 
            plugin: PhotovoltaicPlugin
            ) -> None:
        self.plugin: PhotovoltaicPlugin = plugin

    def export_nominal_power(
            self
            ) -> None:
        '''Export nominal power for LCA calculations.'''
        self.plugin.insert_queue.append(
            {'key': 'LCA - Exports', 'subkey': 'PV Nominal Power', 'value': self.plugin.dcf.inp['Photovoltaic']['Nominal Power (kW)']['Value']}
        )
