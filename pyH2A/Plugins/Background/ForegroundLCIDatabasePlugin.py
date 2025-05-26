from pyH2A.Utilities.input_modification import read_textfile
from pyH2A.Plugins.Plugin import Plugin
from pyH2A.DiscountedCashFlow import DiscountedCashFlow
import numpy as np
import pprint as pp
import matplotlib.pyplot as plt
import logging

class ForegroundLCIDatabasePlugin(Plugin):
    '''Class for processing foreground Life Cycle Inventory (LCI) data for Brightway calculation.
    
    This class processes data related to photovoltaic (PV) systems, including solar radiation,
    water demands, and hydrogen production, and creates an LCI database for Brightway.

    Parameters
    ----------
    dcf : object
        Data container object containing input data in the 'inp' attribute.
    print_info : bool
        Flag to print additional information for debugging or logging purposes.
    '''
    
    def __init__(
            self, 
            dcf: DiscountedCashFlow
            ) -> None:
        '''Initializes the ForegroundLCIDatabasePlugin, processes input data, 
        and creates an LCI database.
        
        Parameters
        ----------
        dcf : object
            Data container object containing input data in the 'inp' attribute.
        print_info : bool
            Flag to print additional information for debugging or logging purposes.
        '''

        super().__init__(dcf)

        self.logger = logging.getLogger("pyH2A.Plugins.Background.ForegroundLCIDatabasePlugin")
        self.logger.info("Starting ForegroundLCIDatabasePlugin")

        table_keys = ['Irradiation Used', 'LCA Parameters Photovoltaic']
        self.process_table(table_keys)

        # Calculate total sunlight based on irradiation data
        total_sunlight = self.calculate_sunlight()
        
        # Create the LCI database using the total sunlight and input data
        self.LCI_database(total_sunlight)

    def calculate_sunlight(
            self
            ) -> float:
        '''Calculates the total amount of sunlight based on input data.
        
        Retrieves sunlight irradiation data from the input container and 
        calculates the total sunlight by summing the irradiation values.
        
        Returns
        -------
        float
            The total amount of sunlight in kilowatt-hours (kWh).
        
        Raises
        ------
        ValueError
            If the sunlight data is not in a valid format (i.e., not a 1D array).
        KeyError
            If required sunlight data is missing from the input.
        '''
        
        try:
            # Retrieve sunlight irradiation data (file path or direct value array)
            irradiation_values = self.dcf.inp['Irradiation Used']['Data']['Value']
            
            # If the irradiation values are a string (file path), read data from the file
            if isinstance(irradiation_values, str):
                data = read_textfile(irradiation_values, delimiter='  ')[:, 1]
            else:
                # Convert the data to a NumPy array if it's already a list of values
                sunlight_values_array = np.array(irradiation_values)
            
            # Ensure that the data is a 1D array
            if len(sunlight_values_array.shape) > 1:
                raise ValueError(f"Expected 1D array for sunlight data, but got shape {sunlight_values_array.shape}.")
            
            # Return the total sunlight by summing the values
            return np.sum(sunlight_values_array)
        
        except KeyError as e:
            raise KeyError(f"Missing required key in input: {e}")
        except Exception as e:
            raise RuntimeError(f"Error while calculating sunlight: {e}")

    def get_value(
            self, 
            section: str, 
            parameter: str
            ) -> float:
        '''Retrieves the value of a specific parameter from the input data.
        
        Parameters
        ----------
        section : str
            The section name in the input data.
        parameter : str
            The parameter to retrieve within the section.
        
        Returns
        -------
        float
            The value of the specified parameter.
        
        Raises
        ------
        ValueError
            If the specified section or parameter is missing from the input data.
        '''
        
        try:
            # Retrieve the value from the specified section and parameter
            return self.dcf.inp[section][parameter]['Value']
        except KeyError:
            raise ValueError(f"Missing or invalid parameter: {section} -> {parameter}")

    def LCI_database(
            self, 
            total_amount_sunlight: float
            ) -> None:
        '''Creates the LCI database by associating activities with exchanges.
        
        The LCI database is structured with activities, exchanges, and their relationships,
        which are saved to JSON files for use in Brightway calculations.
        
        Parameters
        ----------
        total_amount_sunlight : float
            The total amount of sunlight used in the calculation (in kilowatt-hours).
        '''
        
        # Define the LCI activities (production of hydrogen and maintenance of parts)
        lci_activities = {
            "activities": [
                {
                    "name": "Production of hydrogen",
                    "location": "GLO",
                    "reference_product": "hydrogen",
                    "unit": "kilogram",
                    "code": "production_of_hydrogen"
                },
                {
                    "name": "Production and maintenance of individual parts",
                    "location": "GLO",
                    "reference_product": "production",
                    "unit": "unit",
                    "code": "production_and_maintenance"
                }
            ]
        }

        # Retrieve specific LCA parameters from input data
        sea_water_demand_m3 = self.get_value('LCA Parameters Photovoltaic', 'Sea water demand (m3)')
        brine_mass_kg = self.get_value('LCA Parameters Photovoltaic', 'Mass of brine (kg)')
        produced_hydrogen_kg = self.get_value('LCA Parameters Photovoltaic', 'H2 produced (kg)')
        produced_oxygen_kg = self.get_value('LCA Parameters Photovoltaic', 'O2 produced (kg)')
        number_of_pv_modules = self.get_value('LCA Parameters Photovoltaic', 'Amount of PV modules')
        electrolyzer_maintenance_production = self.get_value('LCA Parameters Photovoltaic', 'Production and maintenance electrolyzer')

        # Define the LCI exchanges (inputs and outputs for each activity)
        lci_exchanges = {
            "exchanges": [
                # Production of hydrogen exchanges
                {
                    "input": "sunlight",
                    "amount": total_amount_sunlight,
                    "type": "biosphere",
                    "unit": "kilowatt",
                    "activity": "production_of_hydrogen"
                },
                {
                    "input": "sea water",
                    "amount": sea_water_demand_m3,
                    "type": "biosphere",
                    "unit": "cubic meter",
                    "activity": "production_of_hydrogen"
                },
                {
                    "input": "brine",
                    "amount": brine_mass_kg,
                    "type": "byproduct",
                    "unit": "kilogram",
                    "activity": "production_of_hydrogen"
                },
                {
                    "input": "hydrogen",
                    "amount": produced_hydrogen_kg,
                    "type": "production",
                    "unit": "kilogram",
                    "activity": "production_of_hydrogen"
                },
                {
                    "input": "oxygen",
                    "amount": produced_oxygen_kg,
                    "type": "byproduct",
                    "unit": "kilogram",
                    "activity": "production_of_hydrogen"
                },
                # Production and maintenance exchanges
                {
                    "input": "production_pv_panels",
                    "amount": number_of_pv_modules,
                    "type": "production",
                    "unit": "unit",
                    "activity": "production_and_maintenance"
                },
                {
                    "input": "production_battery",
                    "amount": 1.0,
                    "type": "production",
                    "unit": "unit",
                    "activity": "production_and_maintenance"
                },
                {
                    "input": "production_electrolyzer",
                    "amount": electrolyzer_maintenance_production,
                    "type": "technosphere",
                    "unit": "unit",
                    "activity": "production_and_maintenance"
                },
                {
                    "input": "production_reverse_osmosis",
                    "amount": 1.0,
                    "type": "production",
                    "unit": "unit",  # Specify the correct unit
                    "activity": "production_and_maintenance"
                }
            ]
        }

        # Create the LCI database, associating activities with their respective exchanges
        db_name = "foreground_LCI_database"
        lci_database = {}

        # Process activities and add them to the database
        for activity in lci_activities["activities"]:
            activity_code = activity.pop('code')
            lci_database[activity_code] = activity

        # Process exchanges and associate them with activities
        for exchange in lci_exchanges["exchanges"]:
            input_code = exchange.pop('input')
            activity_code = exchange.pop('activity')
            exchange['input'] = (activity_code, input_code)  # Differentiates between the same variables in different activities
            lci_database[activity_code].setdefault('exchanges', []).append(exchange)

        #Optionally, print the LCI database
        pp.pprint(lci_database)
