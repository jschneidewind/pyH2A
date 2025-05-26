import click
from pyH2A.run_pyH2A import command_line_pyH2A
from pyH2A.Utilities.plugin_input_output_processing import Generate_Template_Input_File

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
	'''Command line interface wrapper function.
	'''
	pass

@cli.command()
@click.option('-i', '--input_file', type=str, help='Path to input file.', required = True)
@click.option('-o', '--output_dir', type=str, help='Path to output directory.', required = True)
def run(input_file, output_dir):
	'''Run pyH2A analysis.
	'''
	output = command_line_pyH2A(input_file, output_dir)

@cli.command()
@click.option('-i', '--input_file', type=str, help='Path to input file.', required = True)
@click.option('-o', '--output_file', type=str, help='Path to output file.', required = True)
@click.option('--origin/--no-origin', default = False, help='Include information on which plugin/module requests input.')
@click.option('--comments/--no-comments', default = False, help='Include comments/documentation for each requested input.')
def generate(input_file, output_file, origin, comments):
	'''Generate input file template from minimal input file.
	'''
	Generate_Template_Input_File(input_file, output_file, origin = origin, comment = comments)




