import click
from pyH2A.run_pyH2A import command_line_pyH2A

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
	pass

@cli.command()
@click.option('-i', '--input_file', type=str, help='Path to input file.')
@click.option('-o', '--output_dir', type=str, help='Path to output directory.')
def run(input_file, output_dir):
	'''Run pyH2A analysis.
	'''
	output = command_line_pyH2A(input_file, output_dir)


