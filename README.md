qikfiller
=========

## Installation
```bash
git clone git@github.com:joshainglis/qikfiller.git
cd qikfiller/src
pip install .

# initialise qikfiller
qikfiller init --qik-api-key <your_api_key> --qik_api_url http://<you_company>.qiktimes.com/api/v1/
```

## Creating events.

### Example usage:
Yesterday we did `2 hours` of `'Billable' (TYPE id:1)` `'Web App Development' (CATEGORY id:31)` on the 
`'Resource Planner Feature' (TASK id:27)` for 
`'Bob's Teahouse' (Customer id:5)` from `10am`.
Long form, this would look like:

```bash
qikfiller create --type Billable --task 'Resource Planner Feature' --category 'Web App Development' \
    --date 2017-03-23 --start 10am --duration 2h \
    --description "Worked on the Bob's Teahouse Resource Planner Feature" \
    --jira-id BTH-123
```
But we could also write this in short form to get the same result        

```bash
qikfiller create bill tea:plan app \
    --date -1 --start 10am --duration 2h \
    --description "Worked on the Resource Planner" \
    --jira-id "BTH-302"
```

If you are entering times as you go and know the ids (from previous usage), this can be shortened significantly:

```bash
qikfiller create 1 27 31 10am 12:30
```

This will create a task from 10am-12:30pm. 
The `1`, `27`, `31` are the ids of the `TYPE`, `TASK`, and `CATEGORY` from above.    

## Searching existing events

__As at time of writing the qiktimes api for accessing existing events is broken.
Once that api is fixed, this functionality will be developed further.__
