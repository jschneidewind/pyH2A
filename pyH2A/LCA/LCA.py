"""
This script gives some examples for using the openLCA matrix export in Python.
You need to have NumPy and SciPy installed, e.g. via pip

  pip install -U numpy scipy

Note that all calculations in these examples are currently done with dense
matrices. Sparse matrices are converted to a dense format in these calculations.
If you want to use faster calculations for sparse matrices checkout the direct
and iterative solvers from the SciPy package:

  https://docs.scipy.org/doc/scipy/reference/sparse.linalg.html
"""

import numpy as np
from pyH2A import DiscountedCashFlow
from pyH2A.LCA.LCA_lib import ExportFolder, Matrix, solve 
from pyH2A.Utilities.input_modification import process_table
import pprint as pp
import logging

class LCA:
    '''Wrapper class for life-cycle assessment.
    '''

    def __init__(
            self, 
            matrix_folder: str, 
            dcf: DiscountedCashFlow
            ) -> None:
        '''Initializes the LCA calculation.'''
        self.logger: logging.Logger = logging.getLogger("pyH2A.LCA.LCA")
        self.logger.info("Starting LCA")

        self.folder = self.import_folder(matrix_folder)
        self.tech_index_dict = self.folder.tech_index()
        self.A, self.B, self.C, self.f = self.load_matrices()
        self.build_scaling_vector(dcf)

        self.perform_LCA()
        

    def import_folder(
            self, 
            folder: str
            ) -> ExportFolder:
        '''Imports the LCA data folder and checks if it has impacts.
        '''

        export_folder = ExportFolder(folder, self.logger)

        if not export_folder.has_impacts():
            self.logger.error('no impacts in your export')
            return
        else:
            return export_folder

    def load_matrices(
            self
            ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        '''Loads the matrices from the LCA data folder.
        '''

        A = self.folder.load(Matrix.A)
        B = self.folder.load(Matrix.B)
        C = self.folder.load(Matrix.C)
        f = self.folder.load(Matrix.f)

        return A, B, C, f
    
    def build_scaling_vector(
            self, 
            dcf: DiscountedCashFlow
            ) -> None:
        '''Builds the scaling vector for the LCA calculation.

        ### Adding check that scaling vector is completely populated with data (no zeros).
        '''
        
        table_group = 'LCA'
        self.scaling_vector = np.zeros_like(self.f)
        
        total_H2_production = np.sum(dcf.inp['Technical Operating Parameters and Specifications']['Output per Year at Gate']['Value'])
        self.scaling_vector[0] = total_H2_production

        for key in dcf.inp:
            if table_group in key:
                process_table(dcf.inp, key, 'Value')
                process_LCA_table(self.scaling_vector, dcf.inp[key], self.tech_index_dict, self.logger)

    def perform_LCA(
            self
            ) -> None:
        '''Performs the LCA calculation.

        ### Adding real data export into LCA class instance instead of printing results

        '''

        g = self.B @ self.scaling_vector
        h = self.C @ g

        for i in self.folder.impact_index():
            self.logger.debug(f'{i.impact_name} , {h[i.index]} , {i.impact_unit}')
            

def process_LCA_table(
        scaling_vector : np.ndarray, 
        input_table : dict, 
        tech_index_dict : dict,
        logger: logging.Logger
        ) -> None:
    '''Processes the an LCA table and builds the scaling vector.

    ### Adding unit check and conversion for the scaling vector.

    '''
    for key in input_table:
        uuid = input_table[key]['UUID']
        value = input_table[key]['Value']

        if uuid in tech_index_dict:
            tech_index = tech_index_dict[uuid].index
            scaling_vector[tech_index] = value
        else:
            logger.error(f'UUID {uuid} not found in tech_index_dict')
            continue