from pyH2A.Utilities.input_modification import hourly_to_daily_power
from pyH2A.Plugins.Plugin import Plugin
from pyH2A.DiscountedCashFlow import DiscountedCashFlow
import numpy as np

class ElectrolyzerPlugin(Plugin):
    '''Simulation of hydrogen production using electrolysis.

    Parameters
    ----------
    CAPEX Multiplier > Multiplier > Value : float
        Multiplier to describe cost reduction of electrolyzer CAPEX for every ten-fold
    Electrolyzer > Nominal Power (kW) > Value : float
        Nominal power of electrolyzer in kW.
    Electrolyzer > Power requirement increase per year > Value : float
        Yearly increase in electrolyzer power demand. Value > 0.
    Electrolyzer > Minimum capacity > Value : float
        Minimum capacity of electrolyzer. Value between 0 and 1.
    Electrolyzer > Conversion efficiency (kg H2/kWh) > Value : float
        Conversion efficiency of electrolyzer. Value > 0.
    Electrolyzer > CAPEX Reference Power (kW) > Value : float
        Reference power of electrolyzer for cost reduction calculations.
    Electrolyzer > Replacement time (h) > Value : float
        Replacement time of electrolyzer stack in hours.
    Financial Input Values > construction time > Value : float
        Construction time of electrolyzer in years.
    Power Generation > Available Power (hourly, kWh) > Value : dict
        Hourly power generation data for electricity production calculation.

    Returns
    -------
    Electrolyzer > H2 Production (yearly, kg) > Value : ndarray
        Yearly hydrogen production in kg.
    Electrolyzer > Yearly Operation Data > Value : ndarray
        Yearly operation data in kWh.
    Electrolyzer > Scaling Factor > Value : float
        CAPEX scaling factor for electrolyzer calculated based on CAPEX multiplier,
        reference and nominal power.
    Planned Replacement > Electrolyzer Stack Replacement > Value : float
        Replacement frequency of electrolyzer stack.
    Power Generation > Available Power (hourly, kWh) > Value : dict
        Available power, hourly basis, dictionary of years (in kWh).
    Power Generation > Available Power (daily, kWh) > Value : dict
        Available power, daily basis, dictionary of years (in kWh).
    Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value : float
        Plant design capacity in kg of H2/day.
    Technical Operating Parameters and Specifications > Operating Capacity Factor (%) > Value : float
        Operating capacity factor in %.
    LCA - Exports > Electrolyzer Nominal Power > Value : float
        Nominal power of electrolyzer in kW.
    '''

    def __init__(
            self, 
            dcf: DiscountedCashFlow
            ) -> None:
        super().__init__(dcf)

        table_keys = ['Financial Input Values', 'CAPEX Multiplier', 'Electrolyzer', 'Power Generation']
        self.process_table(table_keys)
        self.run_plugin()
        self.process_insert_queue()

    def run_plugin(
            self
            ) -> None:
        tea = ElectrolyserPluginTEA(self)
        lca = ElectrolyserPluginLCA(self)

        tea.calculate_H2_production()
        tea.calculate_replacement_frequency()
        lca.export_nominal_power()
        tea.calculate_scaling_factors()

class ElectrolyserPluginTEA:
    '''Handles life-cycle assessment (LCA) calculations for the electrolyser plugin.'''
    def __init__(
            self, 
            plugin: ElectrolyzerPlugin
            ) -> None:
        self.plugin: ElectrolyzerPlugin = plugin
        self.plugin.nominal_power = self.plugin.dcf.inp['Electrolyzer']['Nominal Power (kW)']['Value']

    def calculate_H2_production(
            self
            ) -> None:
        '''Using hourly power generation data and electrolyzer parameters,
        H2 production is calculated.
        '''
        power_generation_yearly_data: dict[np.ndarray] = self.plugin.dcf.inp['Power Generation']['Available Power (hourly, kWh)']['Value']

        yearly_data: list = []
        yearly_data_unused_power: dict = {}
        yearly_data_unused_power_daily: dict = {}

        for year in self.plugin.dcf.operation_years:
            power_generation: np.ndarray = power_generation_yearly_data[year]

            (electrolyzer_power_demand, power_increase) = calculate_electrolyzer_power_demand(
                self.plugin.dcf.inp['Electrolyzer']['Power requirement increase per year']['Value'],
                self.plugin.nominal_power,
                year
            )

            electrolyzer_power_demand *= np.ones(len(power_generation))
            electrolyzer_power_consumption = np.amin(np.c_[power_generation, electrolyzer_power_demand], axis=1)

            threshold = self.plugin.dcf.inp['Electrolyzer']['Minimum capacity']['Value']
            electrolyzer_capacity = electrolyzer_power_consumption / electrolyzer_power_demand
            electrolyzer_capacity[electrolyzer_capacity > threshold] = 1
            electrolyzer_capacity[electrolyzer_capacity <= threshold] = 0

            electrolyzer_power_consumption *= electrolyzer_capacity

            h2_produced = calculate_hydrogen_production(
                electrolyzer_power_consumption,
                self.plugin.dcf.inp['Electrolyzer']['Conversion efficiency (kg H2/kWh)']['Value'],
                power_increase
            )
            
            yearly_data.append([year, np.sum(h2_produced), np.sum(electrolyzer_capacity)])

            # Calculation of unused power
            unused_power = power_generation - electrolyzer_power_consumption
            yearly_data_unused_power[year] = unused_power
            yearly_data_unused_power_daily[year] = hourly_to_daily_power(unused_power)

        yearly_data: np.ndarray = np.asarray(yearly_data)
        self.plugin.operation_hours = yearly_data[:, 2]
        self.plugin.h2_production = np.concatenate([
            np.zeros(self.plugin.dcf.inp['Financial Input Values']['construction time']['Value']), 
            yearly_data[:, 1]
        ])

        # Append the calculated values to the insert queue as dictionaries
        self.plugin.insert_queue.extend([
            {'key': 'Electrolyzer', 'subkey': 'H2 Production (yearly, kg)', 'value': self.plugin.h2_production},
            {'key': 'Technical Operating Parameters and Specifications', 'subkey': 'Plant Design Capacity (kg of H2/day)', 'value': self.plugin.h2_production / 365.},
            {'key': 'Technical Operating Parameters and Specifications', 'subkey': 'Operating Capacity Factor (%)', 'value': 1.},
            {'key': 'Electrolyzer', 'subkey': 'Yearly Operation Data', 'value': yearly_data},
            {'key': 'Power Generation', 'subkey': 'Available Power (hourly, kWh)', 'value': yearly_data_unused_power},
            {'key': 'Power Generation', 'subkey': 'Available Power (daily, kWh)', 'value': yearly_data_unused_power_daily}
        ])

    def calculate_scaling_factors(
            self
            ) -> None:
        '''Calculation of electrolyzer CAPEX scaling factors.'''
        electrolyzer_scaling_factor = self.scaling_factor(
            self.plugin.nominal_power,
            self.plugin.dcf.inp['Electrolyzer']['CAPEX Reference Power (kW)']['Value']
        )
        self.plugin.insert_queue.append(
            {'key': 'Electrolyzer', 'subkey': 'Scaling Factor', 'value': electrolyzer_scaling_factor}
        )
        
    def scaling_factor(
            self, 
            power, 
            reference
            ) -> float:
        '''Calculation of CAPEX scaling factor based on nominal and reference power.'''
        number_of_tenfold_increases = np.log10(power / reference)
        return self.plugin.dcf.inp['CAPEX Multiplier']['Multiplier']['Value'] ** number_of_tenfold_increases
    
    def calculate_replacement_frequency(
            self
            ) -> None:
        '''Calculation of stack replacement frequency for electrolyzer.'''
        replacement_frequency, number_of_replacements = calculate_stack_replacement(
            self.plugin.operation_hours, 
            self.plugin.dcf.inp['Electrolyzer']['Replacement time (h)']['Value']
        )
        # This case needs extra parameters so they are included in the dictionary.
        self.plugin.insert_queue.append(
            {'key': 'Planned Replacement', 'subkey': 'Electrolyzer Stack Replacement', 'field': 'Frequency (years)', 'value': replacement_frequency, 'add_processed': False, 'insert_path': False}
        )

class ElectrolyserPluginLCA:
    def __init__(
            self, 
            plugin: ElectrolyzerPlugin
            ) -> None:
        self.plugin = plugin

    def export_nominal_power(
            self
            ) -> None:
        self.plugin.insert_queue.append(
            {'key': 'LCA - Exports', 'subkey': 'Electrolyzer Nominal Power', 'value': self.plugin.nominal_power}
        )

def calculate_stack_replacement(
        operating_hours, 
        replacement_time
        ) -> tuple[float, float]:
    '''Calculation of stack replacement frequency for electrolyzer.'''
    cumulative_running_time = np.cumsum(operating_hours)
    stack_usage = cumulative_running_time / replacement_time

    number_of_replacements = np.floor_divide(stack_usage[-1], 1)
    replacement_frequency = len(stack_usage) / (number_of_replacements + 1.)
    return replacement_frequency, number_of_replacements

def calculate_hydrogen_production(
        power_consumption: np.ndarray, 
        conversion_efficiency: float, 
        power_increase: float
        ) -> np.ndarray:
    '''Calculation of hydrogen production based on power consumption, conversion efficiency 
    and power increase.
    '''
    return power_consumption * conversion_efficiency / power_increase

def calculate_electrolyzer_power_demand(
        power_requirement_increase: float, 
        nominal_power: float, 
        year: int
        ) -> tuple[float, float]:
    '''Calculation of yearly increase in electrolyzer power demand.'''
    increase = (1. + power_requirement_increase) ** year
    demand = increase * nominal_power
    return demand, increase
