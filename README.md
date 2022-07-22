# Oort Demo
Quick demo to identify parallel sessions in different locations from Okta Logs stream.

## Working with the Tinybird CLI

To start working with data projects as if they were software projects, first install the Tinybird CLI in a virtual environment.
Check the [CLI documentation](https://docs.tinybird.co/cli.html) for other installation options and troubleshooting.

```bash
python3 -mvenv .e
. .e/bin/activate
pip install tinybird-cli
tb auth --interactive
```

Choose your region: __1__ for _us-east_, __2__ for _eu_

Go to your workspace, copy a token with admin rights and paste it. A new `.tinyb` file will be created.



## Data Project

```bash
├── datasources
│   └── log_events.datasource
├── endpoints
│   └── parallel_session_alerts.pipe
├── pipes
```

In the `/datasources` folder, we have one data source to store the Okta logs.

In the `/endpoints` folder, we have one pipe that returns actors with parallel sessions in different locations.

Push the data project to your workspace:

```bash
tb push --push-deps --no-check
```

## Sending dummy events

Go to the `data-generator` folder and run the generator script to simulate a stream of Okta logs:

```bash
python3 data-generator/send_events.py
```

Feel free to play around with any of the flags to modify the events. See `python3 data-generator/send_events.py --help` for all of the different flags.

For generating about 100k events over a range of 1 day, we used:

```bash
python3 data-generator/send_events.py --d_from 1 --sample 987 --events 213 --repeat 100
```

## Token Security

You now have your data project in Tinybird with simulated data.

The endpoints need a [token](https://www.tinybird.co/guide/serverless-analytics-api) to be consumed. You should not expose your admin token, so let's create one with more limited scope:

```bash
pip install jq

TOKEN=$(cat .tinyb | jq '.token'| tr -d '"')
HOST=$(cat .tinyb | jq '.host'| tr -d '"')

curl -H "Authorization: Bearer $TOKEN" \
-d "name=endpoints_token" \
-d "scope=PIPES:READ:parallel_session_alerts" \
$HOST/v0/tokens/
```

You will see a response similar to this:

```json
{
    "token": "<new_token>",
    "scopes": [
        {
            "type": "PIPES:READ",
            "resource": "parallel_session_alerts",
            "filter": ""
        }
    ],
    "name": "endpoints_token"
}
```

## Clean the Workspace

If you want to delete all pipes and datasources, be sure you have them in your local folder `tb pull` and run `tb workspace clear`

```bash
$ tb workspace clear
```
