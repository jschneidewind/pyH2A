import math
from pathlib import PurePath
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
from pyH2A.Utilities.input_modification import file_import

def make_bold(string):
	'''Convert provided string to a string which is formatted to be bold.
	"%" signs cannot be rendered bold with this approach and are hence returned normal'''

	if isinstance(string, str):
		string = string.split(' ')
	elif isinstance(string, float):
		string = [str(string)]

	output = ''

	for word in string:
		if '%' in word:
			output += r'$\bf{' + word[:-1] + '}$' + word[-1] + ' '
		else:
			output += r'$\bf{' + word + '}$' + ' '

	return output

def set_font(font_family, font, font_size):
	'''Set font for plot.

	Parameters
	----------
	font_family : str
		Font family, either 'serif' or 'sans-serif'.
	font : str
		Name of font.
	font_size : float
		Font size.
	'''

	from matplotlib import rcParams

	rcParams['font.family'] = font_family
	rcParams['font.sans-serif'] = [font]
	rcParams['font.size'] = font_size

class Figure_Lean:
	'''Wrapper class for figures.

	Parameters
	----------
	name : str
		Name of figure, used for saving.
	directory : str
		Path to directory where figure is to be saved.
	provided_figure_and_axis : tuple or None, optional
		Tuple of matplotlib.fig and matplotlib.ax objects. If ``None`` new `fig`
		and `ax` objects are generated.
	show : bool, optional
		If True, figure is shown.
	save : bool, optional
		If True, figure is saved.
	pdf : bool, optional
		If True, figure is saved as a PDF file. If False, it is saved as a PNG
		file.
	dpi : int, optional
		Dots per inch resolution of figure.
	transparent : bool, optional
		Flag to control if background of figure is transparent or not.
	nrows : int, optional
		Number of rows for subplots.
	ncols : int, optional
		Number of columns for suplots.
	fig_width : float, optional
		Width of figure in inches.
	fig_height : float, optional
		Height of figure in inches.
	left : float, optional
		Left edge of plot in axis fraction coordinates.
	right : float, optional
		Right edge of plot in axis fraction coordinates.
	top : float, optional
		Top edge of plot in axis fraction coordinates.
	bottom : float, optional
		Bottom edge of plot in axis fraction coordinates.
	wspace : float, optional
		Vertical white space between subplots.
	hspace : float, optional
		Horizontal white space between subplots.
	font_family : str, optional
		Font family, either 'serif' or 'sans-serif'.
	font : str, optional
		Name of font.
	font_size : float, optional
		Font size.
	sharex : bool, optional
		Flag to control if x axis is shared between subplots.

	Notes
	-----
	Provided figure is shown and/or saved in provided directory with given name by
	running `Figure_Lean.execute()`.
	'''
	def __init__(self, name, directory, provided_figure_and_axis = None, 
				 show = False, save = False, 
				 pdf = False, dpi = 150, transparent = False,
				 nrows = 1, ncols = 1, fig_width = 6.4, fig_height = 4.8, 
				 left = 0.125, right = 0.9, top = 0.88, bottom = 0.11, 
				 wspace = 0.2, hspace = 0.2, font_family = 'sans-serif',
				 font = 'Arial', font_size = 12, sharex = False):

		set_font(font_family, font, font_size)

		if provided_figure_and_axis is None:
			fig, ax = plt.subplots(nrows = nrows, ncols = ncols, 
								   figsize = (fig_width, fig_height), sharex = sharex)
		else:
			fig, ax = provided_figure_and_axis

		fig.subplots_adjust(left = left, right = right, top = top, bottom = bottom, 
							wspace = wspace, hspace = hspace)


		self.fig = fig
		self.ax = ax

		self.name = name
		self.directory = directory

		self.show = show
		self.save = save
		self.pdf = pdf
		self.dpi = dpi
		self.transparent = transparent

	def execute(self):
		'''Running `self.execute()` executes desired 
		`show` and `save` options.
		'''
		if self.show:
			plt.show()
		else:
			plt.close()

		if self.save:
			self.save_figure(self.pdf, self.dpi, self.transparent)

	def save_figure(self, pdf, dpi, transparent):
		'''Saving figure in target dictionary with specified 
		parameters.
		'''

		if pdf is True:
			suffix = '.pdf'
		else:
			suffix = '.png'

		path_to_file = PurePath(self.directory, self.name + suffix)

		self.fig.savefig(path_to_file, 
						 transparent = transparent, 
						 dpi = dpi)

		plt.close()

def millify(n, dollar_sign = True):
	'''Converts n to a string with shorthand notation for thousand-steps'''

	millnames = ['','K','M','B','T']
	n = float(n)
	millidx = max(0,min(len(millnames)-1, int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

	if dollar_sign:
		return '${:.2f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
	else:
		return '{:.2f}{}'.format(n / 10**(3 * millidx), millnames[millidx])

class MathTextSciFormatter(mticker.Formatter):
	'''Formatter for scientific notation in MathText.

	Methods
	-------
	__call__:
		Call method.
	fix_minus:
		Fixing minus.
	format_data:
		Format data method.
	format_data_short:
		Format data shortened method.
	format_ticks:
		Format ticks methods.
	'''

	def __init__(self, fmt="%1.1e"):
	    self.fmt = fmt
	def __call__(self, x, pos=None):
		s = self.fmt % x
		decimal_point = '.'
		positive_sign = '+'
		tup = s.split('e')
		significand = tup[0].rstrip(decimal_point)
		sign = tup[1][0].replace(positive_sign, '')
		exponent = tup[1][1:].lstrip('0')
		if exponent:
			exponent = '10^{%s%s}' % (sign, exponent)
		if significand and exponent:
			s =  r'%s{\times}%s' % (significand, exponent)
		else:
			s =  r'%s%s' % (significand, exponent)
		return "${}$".format(s)

def format_scientific(value):
	'''Converts value to string with scientfic (10**x) notation'''

	formatter = MathTextSciFormatter()
	return formatter(value)

def dynamic_value_formatting(value, cutoff = 6):
	'''Dynamic formatiing of value to string.

	Parameters
	----------
	cutoff : int, optional
		Cutoff value for string length. Below cutoff value a
		string is shown without special formatting.

	Notes
	-----
	If value is an int (or a float that can be represented as an int) and its 
	length as a string is less than the `cutoff value`, it will be printed as such.
	If its length as a string is more than the cutoff value, it will be either printed 
	using the `millify` function (if the value is larger than 1), or using the 
	`format_scientific` function (if the value is smaller than 1).
	'''

	if isinstance(value, int) or isinstance(value, np.int64):
		pass
	elif isinstance(value, float):
		if value.is_integer():
			value = int(value)
	else:
		raise ValueError('{0} is non-numeric. type = {1}'.format(value, type(value)))

	if len(str(value)) < cutoff:
		return str(value)
	else:

		if value > 1:
			return millify(value, dollar_sign = False)
		else:
			return format_scientific(value)

def bottom_offset(self, bboxes, bboxes2):
	'''Bottom offset for cost contribution plot labels.
	'''

	pad = plt.rcParams["xtick.major.size"] + plt.rcParams["xtick.major.pad"]
	
	bottom = self.axes.bbox.ymin
	self.offsetText.set(va="top", ha="left") 
	oy = bottom - pad * self.figure.dpi / 72.0
	self.offsetText.set_position((1.02, oy))

def insert_image(path, x, y, zoom, ax):
	'''Insert image into plot.

	Parameters
	----------
	path : str
		Path to image to be inserted.
	x : float
		x axis coordinate of image in axis fraction coordinates.
	y : float
		y axis coordinate of image in axis fraction coordinates.
	ax : matplotlib.ax
		matplotlib.ax object into which image is inserted.
	'''

	img = mpimg.imread(file_import(path))
	imagebox = OffsetImage(img, zoom = zoom)
	ab = AnnotationBbox(imagebox, (x, y), frameon = False, xycoords = ax.transAxes)
	ax.add_artist(ab)

