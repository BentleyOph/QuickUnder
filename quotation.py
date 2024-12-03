import os
from dotenv import load_dotenv
import openai
import json 

# Load the environment variables
load_dotenv()  
project_id = os.getenv('OPENAI_PROJECT_ID')

# Initialize the OpenAI client
client = openai.OpenAI(
    organization='org-8VjUpT7VbQkqQsqzHTLoa1h0',
    project=project_id
)


# #assume that it has received the response from the completions api 
# proposal_data = {
#     "name_of_reinsured": "First Assurance Company Ltd",
#     "name_of_insured": "Fekan Howell LLP",
#     "occupation_of_insured": "Audit, Tax and Advisory Services (Certified Public Accountants)",
#     "period_of_cover": 2024,
#     "number_of_business_partners": 3,
#     "number_of_staff": 7,
#     "indemnity_and_excess": {
#         "indemnity": 100000000.0,
#         "excess": 250000.0
#     },
#     "extra_covers": {
#         "libel_and_slander": "false",
#         "loss_of_documents": "true",
#         "dishonesty_of_employees": "false"
#     },
#     "revenues": {
#         "year_2022": 5000000.0,
#         "year_2023": 7000000.0,
#         "estimated_income": 10000000.0
#     }
#     }

def calculate_quotation(proposal_data):
    proposal_data = json.loads(proposal_data)
    # Step 1: Get values from proposal data
    partners = proposal_data['number_of_business_partners']
    staff = proposal_data['number_of_staff']
    indemnity = proposal_data['indemnity_and_excess']['indemnity']
    annual_fees = indemnity
    
    # Step 2: Calculate partner and staff costs
    cost_of_principals = partners * 3600
    cost_of_qualified_assistants = staff * 3000
    total_staff_cost = cost_of_principals + cost_of_qualified_assistants
    
    # Step 3: Determine the fee-based rate
    if annual_fees <= 1_000_000:
        rate = 0.0105
    elif annual_fees <= 2_000_000:
        rate = 0.0075
    elif annual_fees <= 5_000_000:
        rate = 0.0045
    elif annual_fees <= 10_000_000:
        rate = 0.0035
    elif annual_fees <= 20_000_000:
        rate = 0.00225
    else:
        rate = 0.00125
    
    fee_based_premium = annual_fees * rate
    
    # Step 4: Calculate increased limit of indemnity loading
    if indemnity == 1_000_000:
        indemnity_loading = 1.0
    elif indemnity == 2_500_000:
        indemnity_loading = 1.5
    elif indemnity == 5_000_000:
        indemnity_loading = 1.9
    elif indemnity == 10_000_000:
        indemnity_loading = 2.3
    elif indemnity == 20_000_000:
        indemnity_loading = 2.75
    elif indemnity == 40_000_000:
        indemnity_loading = 3.25
    elif indemnity == 60_000_000:
        indemnity_loading = 3.65
    else:
        indemnity_loading = 4.5  # For indemnity greater than 60M (defaulting to 100M)
    

    total_A = fee_based_premium + total_staff_cost
    
    indemnity_premium = indemnity_loading * total_A

    total_B = indemnity_premium

    
    # Step 5: Apply category of profession multiplier  #TO BE AI DETERMINED
    # Define the profession multiplier mapping based on the rates provided
    profession_multiplier_map = {
        "optician": 1.00,
        "chemist": 1.00,
        "accountant": 1.00,
        "auditor": 1.00,
        "attorney": 1.00,
        "architect": 1.35,
        "civil engineer": 1.35,
        "quantity surveyor": 1.35,
        "dentist": 1.75,
        "doctor": 1.75,
        "surgeon": 1.75
    }

    # Assume that the proposal_data contains the occupation of the insured
    occupation = proposal_data["occupation_of_insured"]

    # Normalize the occupation string to lowercase to handle case-insensitive matching
    occupation_normalized = occupation.lower()

    # Default to 1.00 if no profession is found
    profession_multiplier = 1.00

    # Check if any profession from the profession_multiplier_map is in the occupation string
    for profession, multiplier in profession_multiplier_map.items():
        if profession in occupation_normalized:
            profession_multiplier = multiplier
            break  # Stop searching once a match is found

    # Apply the profession multiplier to premium B
    total_C = total_B * profession_multiplier  # premium_B is the value of total_B

    # Calculate the basic premium
    basic_premium = total_A + total_B + total_C

    

    # print(proposal_data['extra_covers']['loss_of_documents'])
    # print(proposal_data['extra_covers']['dishonesty_of_employees'])
    # print(proposal_data['extra_covers']['libel_and_slander'])

    # Step 6: Calculate extensions
    extension_loss_of_documents = 0.10 * basic_premium if proposal_data['extra_covers']['loss_of_documents'] else 0
    extension_dishonesty_of_employees = 0.10 * basic_premium if proposal_data['extra_covers']['dishonesty_of_employees'] else 0
    extension_libel_and_slander = 0.10 * basic_premium if proposal_data['extra_covers']['libel_and_slander'] else 0
    
    total_extensions = extension_loss_of_documents + extension_dishonesty_of_employees + extension_libel_and_slander
    
    # Step 7: Calculate total premium
    total_basic_premium = basic_premium + total_extensions
    
    # Levies and SD as in the image
    levies = total_basic_premium * 0.0045 
    sd = 40.00  # Fixed stamp duty
    
    total_premium = total_basic_premium + levies + sd
    
    # Return the detailed breakdown as a dictionary
    return {
        "name_of_reinsured": proposal_data["name_of_reinsured"],
        "name_of_insured": proposal_data["name_of_insured"],
        "occupation_of_insured": proposal_data["occupation_of_insured"],
        "number_of_business_partners": proposal_data["number_of_business_partners"],
        "number_of_staff": proposal_data["number_of_staff"],
        "indemnity_limit": indemnity,
        "period_of_cover": proposal_data["period_of_cover"],
        "cost_of_principals": cost_of_principals,
        "cost_of_qualified_assistants": cost_of_qualified_assistants,
        "total_staff_cost": total_staff_cost,
        "fee_based_premium": fee_based_premium,
        "indemnity_loading": indemnity_loading,
        "indemnity_premium": indemnity_premium,
        "basic_premium": basic_premium,
        "extensions": {
            "loss_of_documents": extension_loss_of_documents,
            "dishonesty_of_employees": extension_dishonesty_of_employees,
            "libel_and_slander": extension_libel_and_slander
        },
        "total_extensions": total_extensions,
        "total_basic_premium": total_basic_premium,
        "levies": levies,
        "stamp_duty": sd,
        "total_premium": total_premium
    }

# # Example usage
# result = calculate_quotation(proposal_data)
# print(result)


# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "calculate_quotation",
#             "description": "Calculates the professional indemnity quotation based on partners, assistants, and indemnity limits.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "partners_rate": {
#                         "type": "number",
#                         "description": "The rate for each partner."
#                     },
#                     "qualified_assistants_rate": {
#                         "type": "number",
#                         "description": "The rate for each qualified assistant."
#                     },
#                     "unqualified_assistants_rate": {
#                         "type": "number",
#                         "description": "The rate for each unqualified assistant."
#                     },
#                     "annual_fees": {
#                         "type": "number",
#                         "description": "Annual fees based on estimated income."
#                     },
#                     "indemnity": {
#                         "type": "number",
#                         "description": "The limit of indemnity."
#                     },
#                     "excess": {
#                         "type": "number",
#                         "description": "The excess or deductible limit."
#                     },
#                     "profession_rate": {
#                         "type": "number",
#                         "description": "The percentage rate based on the profession of the insured."
#                     }
#                 },
#                 "required": ["partners_rate", "qualified_assistants_rate", "annual_fees", "indemnity", "profession_rate"],
#                 "additionalProperties": False
#             }
#         }
#     }
# ]

# messages = [
#     {"role": "system", "content": "You are a helpful assistant to calculate professional indemnity quotations."},
#     {"role": "user", "content": "Please calculate the quotation based on the following parameters: partners rate 3000, qualified assistants rate 2500, annual fees 100000000, limit of indemnity 100000000, profession rate 100%."}
# ]

# response = client.chat.completions.create(
#     model='gpt-4o-2024-08-06',
#     messages=messages,
#     tools=tools
# )

# # Handle the response
# print(response)




