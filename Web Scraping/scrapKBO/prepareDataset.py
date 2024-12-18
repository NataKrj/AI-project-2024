import pandas as pd

file_paths = [
    'company_status_random_sample_2500_1.csv',
    'company_status_random_sample_2500_2.csv',
    'company_status_random_sample_2500_3.csv',
    'company_status_random_sample_2500_4.csv',
    'company_status_random_sample_2500_5.csv'
]

statuses_to_keep = {
    "not found in KBO data table",
    "ENT LP Stopped",
    "EU Stopped",
    "ENT LP Active",
    "EU Active"
}

filtered_df = pd.concat(
    (pd.read_csv(file).query("Status in @statuses_to_keep") for file in file_paths),
    ignore_index=True
)

filtered_df.to_csv('filtered_file_random_2500.csv', index=False)
print("Done: 'filtered_file_random_2500.csv'")
