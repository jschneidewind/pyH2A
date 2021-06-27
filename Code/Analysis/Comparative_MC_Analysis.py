import matplotlib.pyplot as plt
import numpy as np
from Analysis.Monte_Carlo_Analysis import Monte_Carlo_Analysis
from input_modification import convert_input_to_dictionary
from output_utilities import insert_image, Figure_Lean
import pprint

class Comparative_MC_Analysis:

	def __init__(self, input_file):
		self.inp = convert_input_to_dictionary(input_file)
		self.models = self.get_models()
		self.check_target_price_range_consistency()

	def get_models(self):

		models = {}

		for key, input_file in self.inp['Comparative_MC_Analysis'].items():
			model = Monte_Carlo_Analysis(input_file['Value'])

			models[key] = {}
			models[key]['Model'] = model

			try:
				models[key]['Image'] = input_file['Image']
			except KeyError:
				pass

		return models

	def check_target_price_range_consistency(self):

		model_keys = list(self.models)

		target_price_range = np.asarray(self.models[model_keys[0]]['Model'].target_price_range)
		for model_key in model_keys[1:]:
			model_range = self.models[model_key]['Model'].target_price_range
			assert np.array_equal(target_price_range, model_range), 'Target price ranges differ between input files. Reference: {0}, model: {1}'.format(target_price_range, model_range)

	def plot_comparative_distance_histogram(self, fig_width = 11, **kwargs):

		model_number = len(self.models)

		fig, ax = plt.subplots(model_number, 1, figsize = (fig_width, 1.7 * model_number), sharex = True)
		fig.subplots_adjust(left = 0.2, right = 0.55, hspace = 0.2, top = 0.9, bottom = 0.15)

		for counter, (model_name, model) in enumerate(self.models.items()):

			if counter == 0:
				model['Model'].plot_distance_histogram(ax = ax[counter], fig = fig, figure_lean = False)
			if counter == model_number -1:
				model['Model'].plot_distance_histogram(ax = ax[counter], xlabel = True, figure_lean = False)
			else:
				model['Model'].plot_distance_histogram(ax = ax[counter], figure_lean = False)

			if 'Image' in model:
				insert_image(model['Image'], -0.35, 0.5, 0.08, ax[counter])

		Figure_Lean(fig, 'Monte_Carlo_Comparative_Distance_Histogram', **kwargs)

		return fig

	def plot_comparative_distance_cost_relationship(self, **kwargs):

		model_number = len(self.models)

		fig, ax = plt.subplots(figsize = (10,6))
		fig.subplots_adjust(right = 0.43, left = 0.08, top = 0.92)

		ax.set_ylim(0, 8.)
		ax.plot([0, 1], [1.5, 1.5], '--', color = 'black')

		for counter, (model_name, model) in enumerate(self.models.items()):
			ycoord = 1 - 1.1 * (counter / model_number) - 0.23

			model['Model'].plot_distance_cost_relationship(figure_lean = False, ax = ax, ycoord = ycoord)

			if 'Image' in model:
				insert_image(model['Image'], 1.2, ycoord + 0.12, 0.08, ax)

		Figure_Lean(fig, 'Monte_Carlo_Comparative_Distance_Cost_Relationship', **kwargs)

		return fig

	