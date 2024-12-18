import pandas as pd

file_path = 'company_list.csv'
df = pd.read_csv(file_path, encoding='latin-1', sep=';', skip_blank_lines=True)
df = df.dropna(how='all')
random_sample = df.sample(n=2500, random_state=42)
random_sample.to_csv('random_sample_2500.csv', index=False)
print("Fin 2500 random companies")