from pyH2A.Utilities.input_modification import insert, process_table, hourly_to_daily_power
import numpy as np

input_dict = {
    "Financial Input Values": {
        "Construction time": {
            "Value": {
                "type": {int,},
                "bounds": (0, 40),
            },
            "Unit": {
                "dimension": "time",
                "enforced_unit": "year",
            },
            "optional": False,
            "description": "Construction time of hydrogen production plant."
        },
    },
    "CAPEX Multiplier": {
        "Multiplier": {
            "Value": {
                "type": {float,},
                "bounds": (0, None),
            },
            "Unit": {
                "dimension": "dimensionless",
            },
            "optional": False,
            "description": "Multiplier to describe cost reduction of electrolysis CAPEX for every ten-fold increase of power relative to CAPEX reference power. Based on the multiplier the CAPEX scaling factor is calculated as: multiplier ^ (number of ten-fold increases). A value of 1 leads to no CAPEX reduction, a value < 1 enables cost reduction."
        },
    },
    "Electrolyzer": {
        "Nominal power": {
            "Value": {
                "type": {float,},
                "bounds": (0, None),
            },
            "Unit": {
                "dimension": "power",
            },
            "optional": False,
            "description": "Nominal power of electrolyzer."
        },
        "CAPEX reference power": {
            "Value": {
                "type": {float,},
                "bounds": (0, None),
            },
            "Unit": {
                "dimension": "power",
            },
            "optional": False,
            "description": "Reference power of electrolyzer for cost reduction calculation."
        },
        "Unit nominal power": {
            "Value": {
                "type": {float,},
                "bounds": (0, None),
            },
            "Unit": {
                "dimension": "power",
            },
            "optional": True,
            "description": "Nominal power of one electrolyzer unit for unit-count calculation."
        },
        "Power requirement increase per year": {
            "Value": {
                "type": {float,},
                "bounds": (0, None),
            },
            "Unit": {
                "dimension": "dimensionless",
            },
            "optional": False,
            "description": "Electrolyzer power requirement increase per year due to stack degradation. Percentage or value > 0. Increase calculated as: (1 + increase per year) ^ year."
        },
        "Minimum capacity": {
            "Value": {
                "type": {float,},
                "bounds": (0, 1),
            },
            "Unit": {
                "dimension": "dimensionless",
            },
            "optional": False,
            "description": "Minimum capacity required for electrolyzer operation. Percentage or value between 0 and 1."
        },
        "Hydrogen yield per unit energy": {
            "Value": {
                "type": {float,},
                "bounds": (0, None),
            },
            "Unit": {
                "dimension": "mass / energy",
            },
            "optional": False,
            "description": "Electrical conversion efficiency of electrolyzer in mass(H2)/energy(electrical)."
        },
        "Replacement time": {
            "Value": {
                "type": {float,},
                "bounds": (0, None),
            },
            "Unit": {
                "dimension": "time",
            },
            "optional": False,
            "description": "Operating time before stack replacement of electrolyzer is required."
        },
    },
    "Power Generation": {
        "Available energy (hourly)": {
            "Value": {
                "type": {dict,},
                "bounds": (0, None),
            },
            "Unit": {
                "dimension": "energy",
            },
            "optional": False,
            "description": "Available energy, hourly basis, dictionary of years in (energy)."
        },
    },
}

class Electrolyzer_Plugin:
    '''Simulation of hydrogen production using electrolysis.

    Parameters
    ----------
    Financial Input Values > construction time > Value : int
        Construction time of hydrogen production plant in years.
    CAPEX Multiplier > Multiplier > Value : float
        Multiplier to describe cost reduction of electrolysis CAPEX for every ten-fold
        increase of power relative to CAPEX reference power. Based on the multiplier the CAPEX
        scaling factor is calculated as: multiplier ^ (number of ten-fold increases). A value
        of 1 leads to no CAPEX reduction, a value < 1 enables cost reduction.
    Electrolyzer > Nominal Power (kW) > Value : float
        Nominal power of electrolyzer in kW.
    Electrolyzer > CAPEX Reference Power (kW) > Value : float
        Reference power of electrolyzer in kW for cost reduction calculation.
    Electrolyzer > Unit Nominal Power (kW) > Value : float, optional
        Nominal power of one electrolyzer unit in kW. If not provided, CAPEX Reference
        Power (kW) is used as fallback for unit-count calculation.
    Electrolyzer > Power requirement increase per year > Value : float
        Electrolyzer power requirement increase per year due to stack degradation. Percentage 
        or value > 0. Increase calculated as: (1 + increase per year) ^ year.
    Electrolyzer > Minimum capacity > Value : float
        Minimum capacity required for electrolyzer operation. Percentage or value between 0 and 1.
    Electrolyzer > Conversion efficiency (kg H2/kWh) > Value : float
        Electrical conversion efficiency of electrolyzer in (kg H2)/kWh.
    Electrolyzer > Replacement time (h) > Value : float
        Operating time in hours before stack replacement of electrolyzer is required.
    Power Generation > Available Power (hourly, kWh) > Value : dict
        Available power, hourly basis, dictionary of years (in kWh).

    Returns
    -------
    Technical Operating Parameters and Specifications > Plant Design Capacity (kg of H2/day) > Value : nd.array
        Plant design capacity in (kg of H2)/day calculated from installed 
        electrolysis power capacity and hourly power generation data.
    Technical Operating Parameters and Specifications >	Operating Capacity Factor (%) > Value : float
        Operating capacity factor is set to 1 (100%).
    Planned Replacement > Electrolyzer Stack Replacement > Frequency (years) : float
        Frequency of electrolyzer stack replacements in years, calculated from replacement time and hourly
        irradiation data.
    Electrolyzer > Scaling Factor > Value : float
        CAPEX scaling factor for electrolyzer calculated based on CAPEX multiplier, 
        reference and nominal power.
    Electrolyzer > Yearly Operation Data > Value : nd.array
        Yearly operation data of electrolyzer in (year, H2 produced, electrolyzer capacity) format.
    Electrolyzer > H2 Production (yearly, kg) > Value : nd.array
        Yearly hydrogen production in kg.
    Electrolyzer > Number of electrolyzers required > Value : float
        Number of electrolyzer units required, calculated as total nominal
        electrolyzer power divided by unit nominal power.
    Power Generation > Available Power (hourly, kWh) > Value : dict
        Available power (hourly, kWh) after subtracting power consumed by electrolyzer. 
        (dictionary of years).
    Power Generation > Available Power (daily, kWh) > Value : dict
        Available power (daily, kWh) after subtracting power consumed by electrolyzer.
    '''

    def __init__(self, dcf, print_info):
        process_table(dcf.inp, 'CAPEX Multiplier', 'Value')
        process_table(dcf.inp, 'Electrolyzer', 'Value')
        process_table(dcf.inp, 'Power Generation', 'Value')

        self.calculate_H2_production(dcf)
        self.replacement_frequency = calculate_stack_replacement(self.yearly_data[:,2], 
                                    dcf.inp['Electrolyzer']['Replacement time (h)']['Value'])
        self.calculate_scaling_factors(dcf)
        self.calculate_number_of_electrolyzers_required(dcf)

        insert(dcf, 'Technical Operating Parameters and Specifications', 'Plant Design Capacity (kg of H2/day)', 'Value', 
                self.h2_production/365., __name__, print_info = print_info)
        insert(dcf, 'Technical Operating Parameters and Specifications', 'Operating Capacity Factor (%)', 'Value', 
                1., __name__, print_info = print_info)

        insert(dcf, 'Planned Replacement', 'Electrolyzer Stack Replacement', 'Frequency (years)', 
                self.replacement_frequency, __name__, print_info = print_info, add_processed = False,
                insert_path = False)

        insert(dcf, 'Electrolyzer', 'Scaling Factor', 'Value', 
                self.electrolyzer_scaling_factor, __name__, print_info = print_info)
        insert(dcf, 'Electrolyzer', 'Yearly Operation Data', 'Value',
               self.yearly_data, __name__, print_info = print_info)
        insert(dcf, 'Electrolyzer','H2 Production (yearly, kg)', 'Value',
                self.h2_production, __name__, print_info = print_info)
        insert(dcf, 'Electrolyzer', 'Number of electrolyzers required', 'Value',
            self.number_of_electrolyzers_required, __name__, print_info = print_info)

        insert(dcf, 'Power Generation', 'Available Power (hourly, kWh)', 'Value',
                self.yearly_data_unused_power, __name__, print_info = print_info)
        insert(dcf, 'Power Generation', 'Available Power (daily, kWh)', 'Value',
                self.yearly_data_unused_power_daily, __name__, print_info = print_info)

    def calculate_H2_production(self, dcf):
        '''Using hourly power generation data and electrolyzer parameters,
        H2 production is calculated.
        '''

        power_generation_yearly_data = dcf.inp['Power Generation']['Available Power (hourly, kWh)']['Value']

        yearly_data = []
        yearly_data_unused_power = {}
        yearly_data_unused_power_daily = {}

        for year in dcf.operation_years:

            power_generation = power_generation_yearly_data[year]

            electrolyzer_power_demand, power_increase = calculate_electrolyzer_power_demand(dcf.inp['Electrolyzer']['Power requirement increase per year']['Value'],
                                                                                            dcf.inp['Electrolyzer']['Nominal Power (kW)']['Value'],
                                                                                            year)

            electrolyzer_power_demand *= np.ones(len(power_generation))
            electrolyzer_power_consumption = np.amin(np.c_[power_generation, electrolyzer_power_demand], axis = 1)

            threshold = dcf.inp['Electrolyzer']['Minimum capacity']['Value']
            electrolyzer_capacity = electrolyzer_power_consumption / electrolyzer_power_demand
            electrolyzer_capacity[electrolyzer_capacity > threshold] = 1
            electrolyzer_capacity[electrolyzer_capacity <= threshold] = 0

            electrolyzer_power_consumption *= electrolyzer_capacity

            h2_produced = calculate_hydrogen_production(electrolyzer_power_consumption,
                                                        dcf.inp['Electrolyzer']['Conversion efficiency (kg H2/kWh)']['Value'],
                                                        power_increase)
            
            yearly_data.append([year, np.sum(h2_produced), np.sum(electrolyzer_capacity)])

            # Calculation of unused power
            unused_power = power_generation - electrolyzer_power_consumption
            yearly_data_unused_power[year] = unused_power
            yearly_data_unused_power_daily[year] = hourly_to_daily_power(unused_power)

        self.yearly_data = np.asarray(yearly_data)
        self.h2_production = np.concatenate([np.zeros(dcf.inp['Financial Input Values']['construction time']['Value']), 
                                                self.yearly_data[:,1]])
        self.yearly_data_unused_power = yearly_data_unused_power
        self.yearly_data_unused_power_daily = yearly_data_unused_power_daily

    def calculate_scaling_factors(self, dcf):
        '''Calculation of electrolyzer CAPEX scaling factors.
        '''

        self.electrolyzer_scaling_factor = self.scaling_factor(dcf, dcf.inp['Electrolyzer']['Nominal Power (kW)']['Value'], dcf.inp['Electrolyzer']['CAPEX Reference Power (kW)']['Value'])
        
    def scaling_factor(self, dcf, power, reference):
        '''Calculation of CAPEX scaling factor based on nominal and reference power.
        '''
        
        number_of_tenfold_increases = np.log10(power/reference)

        return dcf.inp['CAPEX Multiplier']['Multiplier']['Value'] ** number_of_tenfold_increases

    def calculate_number_of_electrolyzers_required(self, dcf):
        '''Calculation of required number of electrolyzer units.
        '''

        total_power = dcf.inp['Electrolyzer']['Nominal Power (kW)']['Value']

        if 'Unit Nominal Power (kW)' in dcf.inp['Electrolyzer']:
            unit_power = dcf.inp['Electrolyzer']['Unit Nominal Power (kW)']['Value']
        else:
            unit_power = dcf.inp['Electrolyzer']['CAPEX Reference Power (kW)']['Value']

        self.number_of_electrolyzers_required = total_power / unit_power
    
def calculate_electrolyzer_power_demand(power_requirement_increase, nominal_power, year):
    '''Calculation of yearly increase in electrolyzer power demand.
    '''

    increase = (1. + power_requirement_increase) ** year
    demand = increase * nominal_power

    return demand, increase

def calculate_hydrogen_production(power_consumption, conversion_efficiency, power_increase):
    '''Calculation of hydrogen production based on power consumption, conversion efficiency 
    and power increase.
    '''

    h2_production = power_consumption * conversion_efficiency / power_increase

    return h2_production

def calculate_stack_replacement(operation_hours, replacement_time):
    '''Calculation of stack replacement frequency for electrolyzer.
    '''

    cumulative_running_time = np.cumsum(operation_hours)
    stack_usage = cumulative_running_time / replacement_time

    number_of_replacements = np.floor_divide(stack_usage[-1], 1)
    replacement_frequency = len(stack_usage) / (number_of_replacements + 1.)

    return replacement_frequency