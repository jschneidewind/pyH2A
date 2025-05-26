from pyH2A.Plugins.Plugin import Plugin
from pyH2A.DiscountedCashFlow import DiscountedCashFlow
from pyH2A.Utilities.input_modification import daily_to_yearly_power
from pyH2A.Plugins.Hydrogen.ElectrolyzerPlugin import (
    calculate_electrolyzer_power_demand,
    calculate_hydrogen_production,
    calculate_stack_replacement
)
import numpy as np

HOURS_IN_A_YEAR = 8760

class StoredPowerElectrolysisPlugin(Plugin):
    '''Simulation of hydrogen production using electrolysis.

    Parameters
    ----------
    Electrolysis Using Stored Power > Fraction of stored power used for electrolysis > Value : float
        Fraction of stored power used for electrolysis.
    Electrolyzer > Nominal Power (kW) > Value : float
        Nominal power of electrolyzer in kW.
    Electrolyzer > Power requirement increase per year > Value : float
        Electrolyzer power requirement increase per year due to stack degradation. Percentage 
        or value > 0. Increase calculated as: (1 + increase per year) ^ year.
    Electrolyzer > Minimum capacity > Value : float
        Minimum capacity required for electrolyzer operation. Percentage or value between 0 and 1.
    Electrolyzer > Conversion efficiency (kg H2/kWh) > Value : float
        Electrical conversion efficiency of electrolyzer in (kg H2)/kWh.
    Electrolyzer > Replacement time (h) > Value : float
        Operating time in hours before stack replacement of electrolyzer is required.
    Electrolyzer > Yearly Operation Data > Value : nd.array
        Yearly operation data of electrolyzer in (year, H2 produced, electrolyzer capacity) format.
    Electrolyzer > H2 Production (yearly, kg) > Value : nd.array
        Yearly hydrogen production in kg.
    Power Generation > Stored Power (daily, kWh) > Value : dict
        Power stored in battery daily in kWh (dictionary of years).

    Returns
    -------
    Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value : nd.array
        Plant design capacity in (kg of H2)/day calculated from installed 
        electrolysis power capacity and hourly power generation data.
    Planned Replacement > Electrolyzer Stack Replacement > Frequency (years) : float
        Frequency of electrolyzer stack replacements in years, calculated from replacement time and hourly
        irradiation data.
    Power Consumption > Stored Power Electrolysis (kWh, yearly) > Value : nd.array
        Electricity demand of electrolysis using stored power in kWh per year.
    Power Consumption > Stored Power Electrolysis (kWh, yearly) > Type : str
        Type of power consumer, type is 'on_demand' (only uses stored power).
    '''
    def __init__(
            self, 
            dcf: DiscountedCashFlow
            ) -> None:
        super().__init__(dcf)

        table_keys = ['Electrolysis Using Stored Power', 'Power Generation', 'Electrolyzer']
        self.process_table(table_keys)
        self.run_plugin()
        self.process_insert_queue()

    def run_plugin(
            self
            ) -> None:
        tea = StoredPowerElectrolysisPluginTEA(self)
        tea.calculate_H2_production()
        tea.calculate_replacement()


class StoredPowerElectrolysisPluginTEA:
    '''Handles life-cycle assessment (LCA) calculations for the stored power electrolysis plugin.'''
    def __init__(self, plugin: StoredPowerElectrolysisPlugin) -> None:
        self.plugin: StoredPowerElectrolysisPlugin = plugin

    def calculate_H2_production(
            self
            ) -> None:
        electrolyzer_yearly_data = self.plugin.dcf.inp['Electrolyzer']['Yearly Operation Data']['Value']
        remaining_run_time_per_year_in_hours = HOURS_IN_A_YEAR - electrolyzer_yearly_data[:, 2]
        
        (electrolyzer_power_demand, power_increase) = calculate_electrolyzer_power_demand(
            self.plugin.dcf.inp['Electrolyzer']['Power requirement increase per year']['Value'],
            self.plugin.dcf.inp['Electrolyzer']['Nominal Power (kW)']['Value'],
            self.plugin.dcf.operation_years
        )

        maximum_consumable_power_kWh = remaining_run_time_per_year_in_hours * electrolyzer_power_demand
        
        stored_power = self.plugin.dcf.inp['Power Generation']['Stored Power (daily, kWh)']['Value']
        stored_power_yearly = daily_to_yearly_power(stored_power)

        stored_power_yearly_available_for_use = stored_power_yearly * self.plugin.dcf.inp['Electrolysis Using Stored Power']['Fraction of stored power used for electrolysis']['Value']

        power_consumption_kWh = np.minimum(maximum_consumable_power_kWh, stored_power_yearly_available_for_use)

        # Update hydrogen production
        additional_h2_production_kg = calculate_hydrogen_production(
            power_consumption_kWh, 
            self.plugin.dcf.inp['Electrolyzer']['Conversion efficiency (kg H2/kWh)']['Value'],
            power_increase
        )
        
        old_h2_production_kg = self.plugin.dcf.inp['Electrolyzer']['H2 Production (yearly, kg)']['Value']
        new_h2_production_kg = old_h2_production_kg.copy()
        new_h2_production_kg[-len(additional_h2_production_kg):] += additional_h2_production_kg
        
        # Update operation hours
        additional_operation_hours = power_consumption_kWh / electrolyzer_power_demand
        self.operation_hours = additional_operation_hours + electrolyzer_yearly_data[:, 2]

        # Add insert queue entries as dictionaries
        self.plugin.insert_queue.extend([
            {'key': 'Power Consumption', 'subkey': 'Stored Power Electrolysis (kWh, yearly)', 'value': power_consumption_kWh},
            {'key': 'Technical Operating Parameters and Specifications', 'subkey': 'Plant Design Capacity (kg of H2/day)', 'value': new_h2_production_kg / 365.}
        ])

    def calculate_replacement(
            self
            ) -> None:
        replacement_frequency, _ = calculate_stack_replacement(
            self.operation_hours, 
            self.plugin.dcf.inp['Electrolyzer']['Replacement time (h)']['Value']
        )
        # Instead of direct insert calls, add dictionary entries with extra parameters if needed.
        self.plugin.insert_queue.append(
            {'key': 'Planned Replacement', 'subkey': 'Electrolyzer Stack Replacement', 'value': replacement_frequency, 'field': 'Frequency (years)', 'mod': __name__, 'add_processed': False, 'insert_path': False}
        )
        self.plugin.insert_queue.append(
            {'key': 'Power Consumption', 'subkey': 'Stored Power Electrolysis (kWh, yearly)', 'value': 'on_demand', 'field': 'Type', 'mod': __name__}
        )


class StoredPowerElectrolysisPluginLCA:
    def __init__(
            self, 
            plugin: StoredPowerElectrolysisPlugin
            ) -> None:
        self.plugin: StoredPowerElectrolysisPlugin = plugin
