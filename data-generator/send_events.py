import uuid
import requests
import json
from datetime import datetime, timedelta, date
import click
import random
from faker import Faker
fake = Faker()

def send_event(ds: str, token: str, messages: list, host: str):
  params = {
    'name': ds,
    'token': token,
    'wait': 'false',
    'host': host,
  }
  data = '\n'.join(json.dumps(m) for m in messages)
  r = requests.post(f'{host}/v0/events', params=params, data=data)
  # uncomment the following two lines in case you don't see your data in the datasource
  # print(r.status_code)
  # print(r.text)

@click.command()
@click.option('--datasource', help ='the destination datasource. Default = log_events', default='log_events')
@click.option('--sample', help = 'number of messages simulated in each repetition. Default = 100', type=int, default=100)
@click.option('--events', help = 'number of events per request. Sent as NDJSON in the body. Default = 50', type=int, default=50)
@click.option('--repeat', type=int, default=1)
@click.option('--silent', is_flag=True, default=False)
@click.option('--d_from', help = 'used along d_to to simulate data from the past. d_from lets you select the number of days previous to today for starting the simulation. Default = 0', type=int, default=0)
@click.option('--d_to', help = 'used along d_from to simulate data from the past. d_to lets you select the number of days previous to today for ending the simulation. Default = 0', type=int, default=0)

def send_hfi(datasource,
             sample,
             events,
             repeat,
             silent,
             d_from,
             d_to
             ):

 
  with open ("./.tinyb") as tinyb:
    tb = json.load(tinyb)
    token = tb['token']
    host = tb['host']

  severity_choices = ['DEBUG', 'INFO', 'WARN', 'ERROR']
  eventType_choices = ['user.session.start']

  severity_weights = [random.random() for _ in range(len(severity_choices))]
  eventType_weights = [random.random() for _ in range(len(eventType_choices))]

  for _ in range(repeat):  

    nd = []

    get_actor_dict = {uuid.uuid4().hex: fake.email() for s in range(int(events))}
    
    for s in range(sample):
        
        actor_ids = random.choices(list(get_actor_dict.keys()), k=events)
        severity_list = random.choices(severity_choices,severity_weights,k=events)
        eventType_list = random.choices(eventType_choices,eventType_weights,k=events)
        
        actor_id = actor_ids[s%events]

        if (d_from != 0):
            delta_days=random.randint(d_to,d_from)
            delta_seconds=random.randint(1,3600*24)

        message = {
          'uuid': uuid.uuid4().hex,
          'published': (datetime.utcnow() - timedelta(days=delta_days, seconds=delta_seconds)).isoformat() if (d_from != 0) else datetime.utcnow().isoformat(),
          'eventType': eventType_list[s%events],
          'version': '0',
          'severity': severity_list[s%events],
          'actor': {
            'id': actor_id,
            'type': 'User',
            'alternateId': get_actor_dict[actor_id]
          },
          'client': {
              'geographicalContext': {
                    'postalCode': fake.postcode()
              }
          }
        }

        nd.append(message) 
        if len(nd) == events:
            send_event(datasource, token, nd, host)
            nd = []
        if not(silent):
            print(message) 
    send_event(datasource, token, nd, host)
    nd = []
  print(f'Sent {sample*repeat} events')


if __name__ == '__main__':
    send_hfi()