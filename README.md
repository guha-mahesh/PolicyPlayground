# Policy Playground
## Guha Mahesh, Sota Shimizu, Bhuvan Hospet, Carter Vargas

Welcome to Policy Playground by Pushin' Policy! Our app is designed to empower individuals working with economic public policy by providing data-driven insights to support the legislative process.

Through interactive fiscal and monetary tools, users can explore and predict key economic indicators such as the S&P 500 and GDP. Policy Playground also offers access to historical policy data, politicians’ records, and their associated economic impacts—helping economists, lobbyists, and policymakers make informed decisions with confidence.


## Our tools include:

- AI Models to predict Currency Exchange Rates, Market Indicators such as the SPY or the FTSE, and the GDP/Capita of a country based off of fiscal and monetary policy.
- Policy saving and publishing features for politicians to test out policies and save their favorite "presets" or publish policies to receive feedback from Economists
- Note taking features for Lobbyists to keep track of their conversations with politicians and view the politicians proposed policies and their implications
- Pages for Economists to view historic policies and information regarding how the policy was carried out, when the policies were made, and what the policies accomplished
- Additionally, Economists can also utilize a model which shows them similar policies to the historic policies they have saved

## Deploying the project
To go about starting the project, you simply need to 
1. Clone the repository to your computer
  - `git clone https://github.com/guha-mahesh/FinFluxes.git`
  - `cd FinFluxes`
2. Copy the information in the env template in api/.env.template into a .env file in the same directory
3. Replace "northwind" with "global_database" and put in a password
4. Run `docker build -t finfluxes .` in the FinFluxes directory
5. Run `docker compose up `
6. Visit http://localhost:8501/



## How to use:
- Once you load into the website, **TRAIN THE MODEL**
- choose one of the three users for each of our defined personas
- For the Policy Maker, you have the choice to use the models and features as either a German, Britisher, or American. This will affect what market index you predict in addition to what currency exchagnes are displayed.
- If you would like to track your conversations with politicians:
  1. Select the lobbyist persona with the user of your choice
  2. Enter your politician information and the policies they described
  3. View the implications of their policy and add your notes on it
- If you would like to view historic data regarding policies and their attributes or find previous policies similar to your ideas:
  1. Select the economist with the user of your choice:
  2. Filter through attributes regarding the policy to narrow down to policies applicable to your interests
  3. View save the policy and view similar policies and information about your saved policies.


### We Hope You Enjoy Our App
### View Our Blog [Here](https://bhuvanh66.github.io/Bhuvan-Carter-Guha-Sota_DOC/) to see view our methodologies when creating this project!


