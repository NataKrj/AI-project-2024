import pandas as pd
from fuzzywuzzy import fuzz
import sys

if len(sys.argv) < 2:
    print("Error: No file path provided.")
    sys.exit(1)

uploaded_file_path = sys.argv[1]

url1 = 'https://www.treasury.gov/ofac/downloads/sdn.csv'
url2 = 'https://www.treasury.gov/ofac/downloads/consolidated/cons_alt.csv'

try:
    df1 = pd.read_csv(url1, on_bad_lines='skip')
    sanction_list_url1 = df1.iloc[:, 1].dropna().unique()
except Exception as e:
    print(f"Error loading file {url1}: {e}")
    sys.exit(1)

try:
    df2 = pd.read_csv(url2, on_bad_lines='skip')
    sanction_list_url2 = df2.iloc[:, 3].dropna().unique()
except Exception as e:
    print(f"Error loading file {url2}: {e}")
    sys.exit(1)

sanction_list = list(set(sanction_list_url1) | set(sanction_list_url2))

sanction_list_df = pd.DataFrame({'Sanctioned Names': sanction_list})

try:
    sanction_list_df.to_csv('sanction_list.csv', index=False)
    print("Sanctioned names saved to 'sanction_list.csv'")
except Exception as e:
    print(f"Error saving 'sanction_list.csv': {e}")
    sys.exit(1)

sanction_list_file_path = 'sanction_list.csv'

try:
    companies_df = pd.read_csv(uploaded_file_path)
    if 'Name' not in companies_df.columns:
        print("Error: 'Name' column is missing in the companies file.")
        sys.exit(1)
except Exception as e:
    print(f"Error loading companies file {uploaded_file_path}: {e}")
    sys.exit(1)

try:
    sanction_list_df = pd.read_csv(sanction_list_file_path)
    sanctioned_names = sanction_list_df['Sanctioned Names'].str.lower().tolist()
    if not sanctioned_names:
        print("Error: Sanction list is empty.")
        sys.exit(1)
except Exception as e:
    print(f"Error loading sanction list {sanction_list_file_path}: {e}")
    sys.exit(1)

def approximate_match(name, sanctioned_names, threshold=85):
    name = name.lower()
    for sanctioned_name in sanctioned_names:
        similarity = fuzz.ratio(name, sanctioned_name)
        if similarity >= threshold:
            return 46
    return 0

try:
    companies_df['Score_Step_1'] = companies_df['Name'].apply(
        lambda name: approximate_match(name, sanctioned_names)
    )
except Exception as e:
    print(f"Error processing company data: {e}")
    sys.exit(1)

output_file_path = 'Step_1_evaluated_companies.csv'
try:
    companies_df.to_csv(output_file_path, index=False)
    print(f"Evaluation complete with approximate matching. Results saved to {output_file_path}")
except Exception as e:
    print(f"Error saving results to file {output_file_path}: {e}")
    sys.exit(1)
