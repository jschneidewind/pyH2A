import math
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib import rcParams
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']
rcParams['font.size'] = 12

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

class Figure:
	'''Provided function is used to generate a figure (fig as output), which can then be saved
	in the provided directory.
	'''

	def __init__(self, function, directory, **kwargs):
		self.function = function
		self.directory = directory
		self.name = self.function.__name__
		self.fig = function(**kwargs)

	def show(self):

		plt.show()

	def save(self):

		self.fig.savefig('{0}{1}.png'.format(self.directory, self.name), transparent = True, dpi = 150)
		plt.close()

class Figure_Lean:
	'''Provided function is used to generate a figure (fig as output), which can then be saved
	in the provided directory.
	'''
	def __init__(self, fig, name, directory, show = False, save = False, pdf = False, dpi = 150, transparent = False):
		self.fig = fig
		self.name = name
		self.directory = directory
		
		if show:
			self.show()
		else:
			plt.close()

		if save:
			self.save(pdf, dpi, transparent)

	def show(self):
		plt.show()

	def save(self, pdf, dpi, transparent):

		if pdf is True:
			self.fig.savefig('{0}{1}.pdf'.format(self.directory, self.name), transparent = transparent, dpi = dpi)
		else:
			self.fig.savefig('{0}{1}.png'.format(self.directory, self.name), transparent = transparent, dpi = dpi)
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

def format_scientific(value):
	'''Converts value to string with scientfic (10**x) notation'''

	f = mticker.ScalarFormatter(useOffset=False, useMathText=True)
	g = lambda x,pos : "${}$".format(f._formatSciNotation('%1.1e' % x))
	fmt = mticker.FuncFormatter(g)

	return fmt(value)

def dynamic_value_formatting(value, cutoff = 5):
	'''Dynamic formatiing of value to string.
	If value is an int (or a float that can be represented as an int) and its length as a string is less than
	the cutoff value, it will be printed as such.

	If its length as a string is more than the cutoff value, it will be either printed using the millify function
	(if the value is larger than 1), or using the format_scientific function (if the value is smaller than 1)
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

	pad = plt.rcParams["xtick.major.size"] + plt.rcParams["xtick.major.pad"]
	
	bottom = self.axes.bbox.ymin
	self.offsetText.set(va="top", ha="left") 
	oy = bottom - pad * self.figure.dpi / 72.0
	self.offsetText.set_position((1.02, oy))

def insert_image(path, x, y, zoom, ax):

	img = mpimg.imread(path)
	imagebox = OffsetImage(img, zoom = zoom)
	ab = AnnotationBbox(imagebox, (x, y), frameon = False, xycoords = ax.transAxes)
	ax.add_artist(ab)

