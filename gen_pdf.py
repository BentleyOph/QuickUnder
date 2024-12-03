from fpdf import FPDF

def generate_pdf(quotation_data, output_path):
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Add the logo at the top right corner
    pdf.image('./logo/logo.png', x=160, y=10, w=50)

    # Set title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Professional Indemnity Quotation", ln=True, align="C")

    # Move to next line
    pdf.ln(20)

    # Add details like name of reinsured, insured, occupation, and period of cover
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Quotation Details", ln=True)

    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Name of Reinsured: {quotation_data['name_of_reinsured']}", ln=True)
    pdf.cell(200, 10, txt=f"Name of Insured: {quotation_data['name_of_insured']}", ln=True)
    pdf.cell(200, 10, txt=f"Occupation of Insured: {quotation_data['occupation_of_insured']}", ln=True)
    pdf.cell(200, 10, txt=f"Period of Cover: {quotation_data['period_of_cover']}", ln=True)

    # Add summary information
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Summary of Quotation", ln=True)

    # Set font for body text
    pdf.set_font("Arial", '', 12)

    # Fill in the necessary fields
    pdf.cell(200, 10, txt=f"Cost of Principals: {quotation_data['cost_of_principals']}", ln=True)
    pdf.cell(200, 10, txt=f"Cost of Qualified Assistants: {quotation_data['cost_of_qualified_assistants']}", ln=True)
    pdf.cell(200, 10, txt=f"Total Staff Cost: {quotation_data['total_staff_cost']}", ln=True)
    pdf.cell(200, 10, txt=f"Fee Based Premium: {quotation_data['fee_based_premium']:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Indemnity Loading: {quotation_data['indemnity_loading']:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Indemnity Premium: {quotation_data['indemnity_premium']:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Basic Premium: {quotation_data['basic_premium']:.2f}", ln=True)

    # Add Extensions Information
    pdf.cell(200, 10, txt="Extensions:", ln=True)
    pdf.cell(200, 10, txt=f"  - Loss of Documents: {quotation_data['extensions']['loss_of_documents']:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"  - Dishonesty of Employees: {quotation_data['extensions']['dishonesty_of_employees']:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"  - Libel and Slander: {quotation_data['extensions']['libel_and_slander']:.2f}", ln=True)

    # Add Total Premium Breakdown
    pdf.cell(200, 10, txt=f"Total Extensions: {quotation_data['total_extensions']:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Total Basic Premium: {quotation_data['total_basic_premium']:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Levies: {quotation_data['levies']:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Stamp Duty: {quotation_data['stamp_duty']:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Total Premium: {quotation_data['total_premium']:.2f}", ln=True)

    # Add Calculation Breakdown
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Calculation Breakdown", ln=True)

    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Step 1: Principals Cost = {quotation_data['cost_of_principals']} ({quotation_data['number_of_business_partners']} principals * KSh 3,600 each)", ln=True)
    pdf.cell(200, 10, txt=f"Step 2: Qualified Assistants Cost = {quotation_data['cost_of_qualified_assistants']} ({quotation_data['number_of_staff']} * KSh 3,000 each)", ln=True)
    pdf.cell(200, 10, txt=f"Step 3: Total Staff Cost = {quotation_data['total_staff_cost']}", ln=True)
    pdf.cell(200, 10, txt=f"Step 4: Fee Based Premium = {quotation_data['fee_based_premium']} (Based on a fee rate of 0.35%)", ln=True)
    pdf.cell(200, 10, txt=f"Step 5: Indemnity Loading = {quotation_data['indemnity_loading']:.2f} (450% loading for indemnity limit)", ln=True)
    pdf.cell(200, 10, txt=f"Step 6: Indemnity Premium = {quotation_data['indemnity_premium']} (Indemnity loading applied to total A)", ln=True)
    pdf.cell(200, 10, txt=f"Step 7: Basic Premium = {quotation_data['basic_premium']} (Sum of Total A, B, and C)", ln=True)

    # Extensions Breakdown
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Extensions Breakdown:", ln=True)
    pdf.cell(200, 10, txt=f" - Loss of Documents Extension: {quotation_data['extensions']['loss_of_documents']:.2f}", ln=True)
    pdf.cell(200, 10, txt=f" - Dishonesty of Employees Extension: {quotation_data['extensions']['dishonesty_of_employees']:.2f}", ln=True)
    pdf.cell(200, 10, txt=f" - Libel and Slander Extension: {quotation_data['extensions']['libel_and_slander']:.2f}", ln=True)

    # Add any other relevant breakdown information
    pdf.cell(200, 10, txt=f"Levies Calculated at 0.45% of Total Basic Premium", ln=True)
    pdf.cell(200, 10, txt=f"Stamp Duty: KSh 40 (Fixed)", ln=True)
    
    # Save the PDF to a file
    pdf.output(output_path)

