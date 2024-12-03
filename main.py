import os
import streamlit as st
import streamlit_shadcn_ui as ui
from pro_or_loss import process_audited_accounts, print_profit_or_loss
from pdftotext import pdf_to_images, combine_images
from quotation import calculate_quotation
from gen_pdf import generate_pdf
from read_proposal import extract_proposal_data

# Define directories
PROPOSAL_UPLOAD_DIR = './proposals'
AUDIT_UPLOAD_DIR = './audits'
GENERATED_PDF_DIR = './quotations'

# Initialize session state
if 'proposals_processed' not in st.session_state:
    st.session_state['proposals_processed'] = 0
if 'financial_statements_processed' not in st.session_state:
    st.session_state['financial_statements_processed'] = 0
if 'total_premiums' not in st.session_state:
    st.session_state['total_premiums'] = []
if 'proposal_file' not in st.session_state:
    st.session_state['proposal_file'] = None
if 'financial_statement_file' not in st.session_state:
    st.session_state['financial_statement_file'] = None
if 'proposal_data' not in st.session_state:
    st.session_state['proposal_data'] = None
if 'quotation_data' not in st.session_state:
    st.session_state['quotation_data'] = None
if 'pdf_generated' not in st.session_state:
    st.session_state['pdf_generated'] = False
if 'pdf_path' not in st.session_state:
    st.session_state['pdf_path'] = None

def process_files():
    if st.session_state['proposal_file'] and st.session_state['financial_statement_file']:
        # Save files to respective directories
        proposal_pdf_path = os.path.join(PROPOSAL_UPLOAD_DIR, st.session_state['proposal_file'].name)
        with open(proposal_pdf_path, 'wb') as f:
            f.write(st.session_state['proposal_file'].getbuffer())

        audit_pdf_path = os.path.join(AUDIT_UPLOAD_DIR, st.session_state['financial_statement_file'].name)
        with open(audit_pdf_path, 'wb') as f:
            f.write(st.session_state['financial_statement_file'].getbuffer())

        st.success("Files uploaded successfully!")

        # Process the uploaded files if not already done
        if st.session_state['proposal_data'] is None:
            st.write("Processing proposal form...")
            image_paths = pdf_to_images(proposal_pdf_path, './images')
            combined_image = combine_images(image_paths)
            st.session_state['proposal_data'] = extract_proposal_data(combined_image)

        st.write("Proposal Data Extracted:")
        st.json(st.session_state['proposal_data'])

        if st.session_state['quotation_data'] is None:
            st.write("Processing financial statement...")
            is_profit, audit_amount = process_audited_accounts(audit_pdf_path)
            print_profit_or_loss(is_profit, audit_amount)

            if is_profit:
                st.write("Profitable company, proceeding with quotation calculation...")
                data = calculate_quotation(st.session_state['proposal_data'].json())
                st.session_state['quotation_data'] = data
                st.write("Quotation Summary ,amounts in Ksh.:")
                st.json({
                    "Reinsured": data["name_of_reinsured"],
                    "Insured": data["name_of_insured"],
                    "Occupation": data["occupation_of_insured"],
                    "Period of Cover": data["period_of_cover"],
                    "Staff Costs": data["total_staff_cost"],
                    "Basic Premium": data["basic_premium"],
                    "Extensions": data["extensions"],
                    "Total Premium": data["total_premium"],
                })

                # Save the total premium for analytics tracking
                st.session_state['proposals_processed'] += 1
                st.session_state['financial_statements_processed'] += 1
                st.session_state['total_premiums'].append(data["total_premium"])

                pdf_filename = os.path.join(GENERATED_PDF_DIR, f'quotation_{data["name_of_insured"]}.pdf')
                generate_pdf(data, pdf_filename)
                st.session_state['pdf_generated'] = True
                st.session_state['pdf_path'] = pdf_filename

                st.success(f"Quotation PDF generated!")
            else:
                st.error("Quotation denied due to financial losses.")
                st.session_state["financial_statements_processed"] += 1  # Track failed financial statements
        else:
            st.write("Quotation already processed!")
            st.json(st.session_state['quotation_data'])

def main():
    st.title("QuickUnder")
    st.subheader("The Automated Underwriter's dashboard")

    # Using shadcn tabs for Home and Analytics navigation
    tab = ui.tabs(options=['Home', 'Analytics'], default_value='Home', key="tabs")

    if tab == 'Home':
        # File upload for proposal form and financial statements
        col1, col2 = st.columns(2)

        with col1:
            proposal_file = st.file_uploader("Upload Proposal Form", type=["pdf"], key="proposal")
            if proposal_file is not None:
                st.session_state['proposal_file'] = proposal_file

        with col2:
            financial_statement_file = st.file_uploader("Upload Financial Statement", type=["pdf"], key="financial_statement")
            if financial_statement_file is not None:
                st.session_state['financial_statement_file'] = financial_statement_file

        if st.button("Process Files"):
            process_files()

        # Display download button if PDF has been generated
        if st.session_state['pdf_generated'] and st.session_state['pdf_path']:
            with open(st.session_state['pdf_path'], "rb") as pdf_file:
                st.download_button(
                    label="Download Quotation PDF",
                    data=pdf_file,
                    file_name=f'quotation_{st.session_state["quotation_data"]["name_of_insured"]}.pdf',
                    mime='application/pdf'
                )

    elif tab == 'Analytics':
        st.title("Analytics")

        # Display session statistics
        total_proposals = st.session_state["proposals_processed"]
        total_financial_statements = st.session_state["financial_statements_processed"]
        total_premiums = sum(st.session_state["total_premiums"])
        avg_premium = (total_premiums / total_proposals) if total_proposals > 0 else 0

        st.metric("Proposals Processed", total_proposals)
        st.metric("Financial Statements Processed", total_financial_statements)
        st.metric("Total Premium (Ksh)", total_premiums)
        st.metric("Average Premium (Ksh)", avg_premium)

if __name__ == '__main__':
    main()