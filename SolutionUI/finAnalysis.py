import pandas as pd

merged_scores = pd.read_csv('res_sample_KBO.csv')
step_3 = pd.read_csv('Step_3.2_company_analysis_with_scores.csv')

merged_scores.rename(columns={'Name': 'company_name'}, inplace=True)
step_3.rename(columns={'company': 'company_name'}, inplace=True)

step_3_total_scores = step_3.groupby('company_name')['score'].sum().reset_index()
step_3_total_scores.rename(columns={'score': 'Score_Step_3'}, inplace=True)

all_scores = pd.merge(merged_scores[['company_name', 'Score_Step_1', 'Score_Step_2']],
                      step_3_total_scores,
                      on='company_name',
                      how='left')

all_scores = all_scores.fillna(0)

all_scores['total_score'] = all_scores['Score_Step_1'] + all_scores['Score_Step_2'] + all_scores['Score_Step_3']

def assign_risk_level(score):
    if score > 30:
        return 'prohibited'
    elif 7 <= score <= 30:
        return 'high'
    elif 1 <= score <= 6:
        return 'medium'
    elif score < 1:
        return 'low'
    else:
        return 'no risk'

all_scores['risk_level'] = all_scores['total_score'].apply(assign_risk_level)

all_scores.to_csv('Step_4_company_risk_scores.csv', index=False)
print("Risk scoring completed and saved as 'Step_4_company_risk_scores.csv'")
