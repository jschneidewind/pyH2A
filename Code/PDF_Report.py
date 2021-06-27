from fpdf import FPDF

def report(base_case, output_directory, file_name, sensitivity_performed, waterfall_performed):

	pdf = FPDF()
	pdf.set_margins(left = 20, top = 20, right = 20)
	pdf.add_page()
	pdf.set_draw_color(211, 218, 219)	
	
	pdf.set_font('helvetica', 'B', 20)
	pdf.cell(0, 0, 'Total Hydrogen Cost', 0, 2)
	pdf.line(20, 25, 190, 25)
	pdf.cell(0, 10, '', 0, 2)

	pdf.set_font('helvetica', 'B', 12)

	pdf.cell(40, 10, 'Name', 1, 0, 'C')
	pdf.cell(40, 10, 'Value', 1, 2, 'C')

	pdf.cell(-40)
	pdf.set_font('helvetica', '', 12)
	pdf.cell(40, 10, 'Total Cost ($/kg)', 1, 0, 'C')
	pdf.cell(40, 10, '${:.5f}'.format(base_case.h2_cost), 1, 2, 'C')

	pdf.set_font('helvetica', 'B', 20)
	pdf.cell(-40, 10, '', 0, 1)
	pdf.cell(0, 0, 'Graphs', 0, 2)	
	pdf.line(20, 65, 190, 65)

	pdf.image('{0}cost_breakdown.png'.format(output_directory) , None, None, w = 150, h = 0)

	pdf.cell(0, 3, '', 0, 2)
	pdf.set_font('helvetica', 'B', 10)
	pdf.cell(15, 0, 'Figure 1', 0, 0)
	pdf.set_font('helvetica', '', 10)
	pdf.cell(0, 0, 'Cost contributions to total hydrogen cost.', 0, 2)

	if sensitivity_performed is True:
		pdf.cell(-70, 5, '', 0, 1)
		pdf.image('{0}sensitivity_box_plot.png'.format(output_directory) , None, None, w = 170, h = 0)

		pdf.set_font('helvetica', 'B', 10)	
		pdf.cell(15, 0, 'Figure 2', 0, 0)	
		pdf.set_font('helvetica', '', 10)
		pdf.cell(0, 0, 'Sensitivity of hydrogen cost to different parameters.', 0, 2)


	if waterfall_performed is True:
		pdf.add_page()
		pdf.image('{0}waterfall_chart.png'.format(output_directory) , None, None, w = 170, h = 0)

		pdf.set_font('helvetica', 'B', 10)	
		pdf.cell(15, 0, 'Figure 3', 0, 0)	
		pdf.set_font('helvetica', '', 10)
		pdf.cell(0, 0, 'Waterfall chart for hydrogen cost.', 0, 2)

	pdf.output('{0}{1}.pdf'.format(output_directory, file_name), 'F')
