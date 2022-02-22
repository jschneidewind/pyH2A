import matplotlib.pyplot as plt

from pyH2A.Analysis.Comparative_MC_Analysis import Comparative_MC_Analysis
from pyH2A.Utilities.output_utilities import make_bold

import pprint

from matplotlib import rcParams

def toc_figure():

	rcParams['mathtext.fontset'] = 'custom'
	rcParams['mathtext.it'] = 'Arial:italic'
	rcParams['mathtext.bf'] = 'Arial:italic:bold'

	comparative = Comparative_MC_Analysis('./PV_E/Historical_Data/PV_E_Distance_Time.md')

	plot_kwargs = {'show': True, 'save': False, 'pdf': False, 'dpi': 500,
				   'fig_width': 2*2.16535, 'fig_height': 2*1.9685,
				   'left': 0.09, 'right': 0.47, 'bottom': 0.08, 'top': 0.94,
				   'font_size': 17}
	dist_kwargs = {'log_scale': True, 'parameter_table': False,
				   'xlabel_string': r"$\mathbf{Progress}$",
				   'ylabel_string': r"$\mathbf{Hydrogen}$" + " " + r"$\mathbf{cost}$",
				   'linewidth': 4,
				   'ylim': [0.7, 120]}
	image_kwargs = {'x': 1.35, 'zoom': 0.08}

	figure = comparative.plot_comparative_distance_cost_relationship(directory = '.',
															figure_lean = False,
															plot_kwargs = plot_kwargs,
															dist_kwargs = dist_kwargs,
															image_kwargs = image_kwargs)

	ax = figure.ax

	ax.get_legend().remove()
	ax.get_xaxis().set_ticks([])
	ax.get_yaxis().set_ticks([])

	for tick in ax.yaxis.get_minor_ticks():
		tick.set_visible(False)

	ax.spines['top'].set_visible(False)
	ax.spines['right'].set_visible(False)

	ax.spines['bottom'].set_linewidth(3)
	ax.spines['left'].set_linewidth(3)

	ylim = ax.get_ylim()
	xlim = ax.get_xlim()

	ax.set_xlim(xlim)
	ax.set_ylim(ylim)

	ax.plot((xlim[1]), (ylim[0]), ls="", marker=">", ms=11, color="k", clip_on=False)   
	ax.plot((xlim[0]), (ylim[1]), ls="", marker="^", ms=11, color="k", clip_on=False)

	ax.text(1.9, 0.85, r"$\mathbf{PEC}$", color='white', transform = ax.transAxes,
       		 bbox=dict(facecolor='darkred', edgecolor='none', boxstyle='round,pad=0.5'))

	ax.text(1.95, 0.48, r"$\mathbf{PC}$", color='white', transform = ax.transAxes,
       		 bbox=dict(facecolor='darkgreen', edgecolor='none', boxstyle='round,pad=0.5'))

	ax.text(1.85, 0.1, r"$\mathbf{PV+E}$", color='white', transform = ax.transAxes,
       		 bbox=dict(facecolor='darkblue', edgecolor='none', boxstyle='round,pad=0.5'))

	figure.execute()

def main():
	toc_figure()

if __name__ == '__main__':
	main()