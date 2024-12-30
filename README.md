# AI-project-2024
# ADVERSE MEDIA MONITORING AND CLIENT RISK ASSESSMENT SYSTEM
# Team number: 1
## Team members
- Project Manager: Sergejs Kopils 
- Lead Developer:  Diāna Koržaviha
- Developer 1: Natalja Krjuckova
- Developer 2: Agita Ferstere

## Client Overview

Our client is a leading global provider of credit management services. The company focuses on helping businesses recover payments, manage credit risk and ensure financial stability. By providing debt collection services, the client enables businesses to grow while helping individuals manage and overcome debt. Operating in several regions, the client has a significant presence in Belgium, where the majority of its customer base is located.

## Problem Understanding

The client faces increasing challenges in monitoring client activities and assessing risk. With the growth of global markets and complex customer networks, manual risk evaluation is no longer sufficient. Automating risk assessment through adverse media analysis is essential to improve the detection of potential client issues and mitigate financial risks.


## Proposed Solution

To address this challenge, we propose a system for tracking adverse media coverage, evaluating client risk, and verifying company status through active checks and web scraping using APIs. Additionally, the system will conduct company status verification and scoring, ensuring real-time validation. 

This approach reduces manual effort, enhances accuracy, and provides deeper insights into client activities. The solution will help protect the client's reputation, ensure regulatory compliance, and reduce exposure to financial crimes.

## Limitation
The project focus on the Belgian comapanies risk assesment since the client has the most companies registered there and due to  limitations of obtaining information from the registers on the status of companies, since this process is very sensitive and the registers are mostly protected from scraping or under paywall.


## Project Execution
The Project includes 4 step codes in Python for the a system for screening adverse media for risk assessment:
- Inital Framework of the company risk assignment 4 Steps with keywords and risk assessment: https://github.com/NataKrj/AI-project-2024/blob/main/Steps_scoring_Framework.pdf
1. Step: Sanction List check- sanctioned companies check and assign score
2. Step: Company Status check using Selenium library -a company active or not active and assigning scores
3. Step: Web scraping
- Web scraping using API
- Web scraping using Beautiful Soup (Bing)
- Adjusting code with NLP code, sentiment adjustment using VADER
4. Step: Companies score sum of 1+2+3 results with assigned risk level: prohibited, high, medium or low.
- Link to notebook: https://github.com/NataKrj/AI-project-2024/blob/main/Step_1_Step_2_Step_3_Step_4_sanction_list.ipynb
     
## Result
For the result of the scoring of Belgian companies we have made following solutions: 
- UI interface using Tkinter library:  https://github.com/NataKrj/AI-project-2024/tree/main/SolutionUI
- Obtained results load in Mongo database and visualization: https://github.com/NataKrj/AI-project-2024/tree/main/MongoDB%20and%20Visualization
- Mongo database visualization: https://charts.mongodb.com/charts-mongodb-pbuqwjz/public/dashboards/673dbfd4-c3c0-45fb-818c-bec4f2336c73

## Critical Activity contribution of Team members
- Link: [Critical Activity contribution of Team members.pdf](https://github.com/NataKrj/AI-project-2024/blob/main/Critical%20Activity%20contribution%20of%20Team%20members.pdf)
