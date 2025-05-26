from pyH2A.DiscountedCashFlow import DiscountedCashFlow
from pyH2A.Plugins.Plugin import Plugin
import numpy as np


class BatteryPlugin(Plugin):
    '''Simulation of electricity storage using a battery.
    Simulation assumes that battery is charged and completely discharged every day.
    (no electricity storage across days, only one discharge per day, not multiple ones).

    Parameters
    ----------
    Power Generation > Available Power (daily, kWh) > Value : dict
        Available power, daily basis, dictionary of years (in kWh).
    Battery > Design Capacity (kWh) > Value : float
        Full design capacity of battery in kWh.
    Battery > Lowest discharge level > Value : float
        Lowest level to which battery can be discharged. Percentage or value between 0 and 1.
    Battery > Capacity loss per year > Value : float
        Loss of capacity per year. Percentage or value > 0.
    Battery > Round trip efficiency > Value : float
        Round trip efficiency of battery. Percentage or value between 0 and 1.
    
    Returns
    -------
    Power Generation > Stored Power (daily, kWh) > Value : dict
        Power stored in battery daily in kWh (dictionary of years).
    Power Generation > Available Power (daily, kWh) > Value : dict
        Available power, daily basis, dictionary of years (in kWh) - power which 
        has not been stored in battery.
    Power Generation > Available Power (hourly, kWh) > Value : float
        Available power (hourly, kWh) is set to zero, since available power is now 
        only in daily format.
    LCA - Exports > Battery Weight > Value : float
        Weight of battery in kg.
    '''
    def __init__(
            self, 
            dcf: DiscountedCashFlow
            ) -> None:
        super().__init__(dcf)

        table_keys = ['Power Generation', 'Battery']
        self.process_table(table_keys)
        self.run_plugin()
        self.process_insert_queue()

    def run_plugin(
            self
            ) -> None:
        tea = BatteryPluginTEA(self)
        lca = BatteryPluginLCA(self)
        tea.calculate_electricity_storage()
        lca.export_battery_weight()

class BatteryPluginTEA:
    def __init__(
            self, 
            plugin: BatteryPlugin
            ) -> None:
        self.plugin: BatteryPlugin = plugin

    def calculate_electricity_storage(
            self
            ) -> None:
        '''Calculates electricity storage using daily available power.
        '''
        available_power_yearly = self.plugin.dcf.inp['Power Generation']['Available Power (daily, kWh)']['Value']

        yearly_recovered_power = {}
        yearly_unstored_power = {}

        for year in self.plugin.dcf.operation_years:
            daily_available_power = available_power_yearly[year]

            capacity, capacity_decrease = self.calculate_battery_capacity(year)
            # Create an array for capacity that matches the daily available power shape.
            capacity_array = capacity * np.ones(len(daily_available_power))
            # Battery can store at most the minimum of available power and capacity.
            daily_stored_power = np.amin(np.c_[daily_available_power, capacity_array], axis=1)
            daily_recovered_power = daily_stored_power * self.plugin.dcf.inp['Battery']['Round trip efficiency']['Value']

            unstored_power = daily_available_power - daily_stored_power

            yearly_recovered_power[year] = daily_recovered_power
            yearly_unstored_power[year] = unstored_power

        # Append dictionary-based insert queue entries
        self.plugin.insert_queue.extend([
            {'key': 'Power Generation', 'subkey': 'Stored Power (daily, kWh)', 'value': yearly_recovered_power},
            {'key': 'Power Generation', 'subkey': 'Available Power (daily, kWh)', 'value': yearly_unstored_power},
            {'key': 'Power Generation', 'subkey': 'Available Power (hourly, kWh)', 'value': 0}
        ])
    
    def calculate_battery_capacity(
            self, 
            year: int
            ) -> tuple:
        capacity_decrease = (1. - self.plugin.dcf.inp['Battery']['Capacity loss per year']['Value']) ** year
        nominal_capacity = self.plugin.dcf.inp['Battery']['Design Capacity (kWh)']['Value'] * (
            1. - self.plugin.dcf.inp['Battery']['Lowest discharge level']['Value']
        )
        capacity = nominal_capacity * capacity_decrease

        return capacity, capacity_decrease
    

class BatteryPluginLCA:
    def __init__(
            self, 
            plugin: BatteryPlugin
            ) -> None:
        self.plugin: BatteryPlugin = plugin

    def export_battery_weight(
            self
            ) -> None:
        '''Export the weight of the battery.'''
        battery_weight = (
            self.plugin.dcf.inp['Battery']['Weight per capacity (kg/kWh)']['Value'] *
            self.plugin.dcf.inp['Battery']['Design Capacity (kWh)']['Value']
        )
        self.plugin.insert_queue.append(
            {'key': 'LCA - Exports', 'subkey': 'Battery Weight', 'value': battery_weight}
        )
