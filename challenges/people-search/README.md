## Background
One important feature at Rox is the ability to search for people.
In this interview, you will build a similar search feature on mock people data.

## Data
You will be given two CSV files, containing company and people data respectively.
Each person will be working at exactly one company.

## Task
Your task is to implement a function for semantic search over the people data.
In particular, the input will be any natural language search query, and the output will be a list of people that match the query.
Your method should be reasonably fast.

For simplicity, here are some constraints that you can assume:
* The search query will only reference fields that are present in the data. The fields "job title", "seniority", and "industry" will require fuzzy matching.
* The number of distinct values is small for the fields "job title", "seniority", "city", "state", "country", and "industry".
* Queries will only ever require you to filter, sort, or limit the number of results. In particular, you will not have to do any "GROUP BY" aggregations or "OR"-style filters.

## Example Queries
* "Give me all the people at the level of Vice President that work at Googol"
* "I want 10 PMs from San Francisco who have started since August 2024"
* "Who are the CEOs of the top 5 healthcare companies by revenue?"

