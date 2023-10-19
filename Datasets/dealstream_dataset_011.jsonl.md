This dataset contains discussion overview between DealStream and each opportunities on specific dates.


Structure

```
{"messages": [{ "role": "system", "content": "You are a helpful assistant that recognizes the section ID for reference and answers only specifically to a question asked by the user based on the discussions overview under that section ID." },{ "role": "user", "content": "Unique Section ID - dealstream_opportunity_siemens_999001 - This is an overview of the discussions that happened between DealStream and Pfizer on specific date." }, { "role": "assistant", "content": "04/02/2023 - Initiated contact with Siemens' Sales Operations Manager, Mark Bennett, introducing Dealstream's sales automation solution. Scheduled a discovery call for February 10 to explore Siemens' sales challenges."}]}

```
Repeated for each opportunity with out any variation in user content.
Plus general sales data without any repeatations (aggregated_fine_tuning_messages.jsonl)
