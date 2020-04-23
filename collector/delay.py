# coding=utf-8
"""
get request delay
"""
import requests
import pandas as pd
import numpy as np
import pickle
import time
from collections import defaultdict
from configs import application_url, measure_path, application_url_social, application_url_social, measure_path_social, \
    social_services


def get_delay(service, frequency, time_len, ):
    try:
        print(application_url + ':9411/api/v2/traces?limit=350&lookback=' + str(time_len))
        r = requests.get(application_url + ':9411/api/v2/traces?limit=350&lookback=' + str(time_len))
        print(r.status_code)
        r.raise_for_status()
    except Exception as e:
        print('exception in request delay, ', repr(e))
    pickle_file_name = 'json.pkl'  # store it.
    print('start json phrase')
    with open(pickle_file_name, 'wb') as f:
        pickle.dump(r.json(), f)
    dfs = []
    for item in r.json():
        dfs.append(pd.DataFrame(item))
    print('json is valid')
    services_call_time = {} 
    execution_time = {}
    trace_request_time = {}

    trace_id = 0
    for dff in dfs:
        if len(dff) == 1: 
            continue
        time_list = {}
        for index, value in dff.iterrows(): 
            if trace_id not in trace_request_time:
                trace_request_time[trace_id] = value['duration']
            else:
                trace_request_time[trace_id] = max(value['duration'],
                                                   trace_request_time[trace_id])

            if value['kind'] == 'SERVER': 
                name = value['localEndpoint']['serviceName']
                if name not in time_list:
                    time_list[name] = []
                    time_list[name].append(value['duration'])
                else:
                    time_list[name].append(value['duration'])

        if len(time_list) == 0:
            continue
        services_call_time[trace_id] = {}
        execution_time[trace_id] = {}
        for key in time_list:
            short_key = key[3:-8]
            services_call_time[trace_id][short_key] = len(time_list[key])
            execution_time[trace_id][short_key] = np.mean(time_list[key])
        trace_id += 1
    (pd.DataFrame(execution_time) / 1000).T.to_csv(measure_path + service + str(frequency) + '_delay.csv')
    service = service.replace('_', "-")
    return (pd.DataFrame(execution_time) / 1000).T[service].mean()


def get_delay2(service, frequency, time_len, ):
    try:
        print(application_url + ':9411/api/v2/traces?limit=300&lookback=' + str(time_len))
        r = requests.get(application_url + ':9411/api/v2/traces?limit=300&lookback=' + str(time_len))
        print(r.status_code)
        r.raise_for_status()
    except Exception as e:
        print(e)

    # service + str(frequency) + '_delay.csv'
    pickle_file_name = measure_path + service + str(frequency) + '_json.pkl'
    with open(pickle_file_name, 'wb') as f:
        pickle.dump(r.json(), f)
    dfs = []
    for item in r.json():  # ['traceId'] # the trace id
        dfs.append(pd.DataFrame(item))

    services_call_time = {}
    execution_time = {}
    trace_request_time = {} 

    trace_id = 0
    for dff in dfs:
        if len(dff) == 1:
            continue
        time_list = {}  # for record all services time
        for index, value in dff.iterrows():
            if trace_id not in trace_request_time:
                trace_request_time[trace_id] = value['duration']
            else:
                trace_request_time[trace_id] = max(value['duration'],
                                                   trace_request_time[trace_id])

            if value['kind'] == 'SERVER':
                name = value['localEndpoint']['serviceName']
                if name not in time_list:
                    time_list[name] = []
                    time_list[name].append(value['duration'])
                else:
                    time_list[name].append(value['duration'])

        if len(time_list) == 0:
            continue
        services_call_time[trace_id] = {}
        execution_time[trace_id] = {}
        for key in time_list:
            short_key = key[3:-8]
            services_call_time[trace_id][short_key] = len(time_list[key])
            execution_time[trace_id][short_key] = np.mean(time_list[key])
        trace_id += 1

    pd.DataFrame(services_call_time).round(
        2).T.to_csv(measure_path + service + str(frequency) + '_call_times.csv')
    (pd.DataFrame(execution_time) / 1000).T.to_csv(measure_path + service + str(frequency) + '_delay.csv')
    (pd.DataFrame(trace_request_time, index=[
        'value']) / 1000).round(2).T.to_csv(measure_path + service + str(frequency) + 'request_times.csv')

    service = service.replace('_', "-")
    return (pd.DataFrame(execution_time) / 1000).T[service].mean()


def get_delay2_full(service, frequency, req, worker, time_len, ):
    try:
        print(application_url + ':9411/api/v2/traces?limit=300&lookback=' + str(time_len))
        r = requests.get(application_url + ':9411/api/v2/traces?limit=300&lookback=' + str(time_len))
        print(r.status_code)
        r.raise_for_status()
    except Exception as e:
        print(e)

    # service + str(frequency) + '_delay.csv'
    pickle_file_name = measure_path + service + str(frequency) + req + str(worker) + '_json.pkl'
    with open(pickle_file_name, 'wb') as f:
        pickle.dump(r.json(), f)
    dfs = []
    for item in r.json():  # ['traceId'] # the trace id
        dfs.append(pd.DataFrame(item))

    services_call_time = {}
    execution_time = {}
    trace_request_time = {}

    trace_id = 0
    for dff in dfs:
        if len(dff) == 1:
            continue
        time_list = {}  # for record all services time
        for index, value in dff.iterrows():
            if trace_id not in trace_request_time:
                trace_request_time[trace_id] = value['duration']
            else:
                trace_request_time[trace_id] = max(value['duration'],
                                                   trace_request_time[trace_id])

            if value['kind'] == 'SERVER':
                name = value['localEndpoint']['serviceName']
                if name not in time_list:
                    time_list[name] = []
                    time_list[name].append(value['duration'])
                else:
                    time_list[name].append(value['duration'])

        if len(time_list) == 0:
            continue
        services_call_time[trace_id] = {}
        execution_time[trace_id] = {}
        for key in time_list:
            short_key = key[3:-8]
            services_call_time[trace_id][short_key] = len(time_list[key])
            execution_time[trace_id][short_key] = np.mean(time_list[key])
        trace_id += 1

    pd.DataFrame(services_call_time).round(
        2).T.to_csv(measure_path + service + str(frequency) + req + str(worker) + '_call_times.csv')
    (pd.DataFrame(execution_time) / 1000).T.to_csv(
        measure_path + service + str(frequency) + req + str(worker) + '_delay.csv')
    (pd.DataFrame(trace_request_time, index=[
        'value']) / 1000).round(2).T.to_csv(
        measure_path + service + str(frequency) + req + str(worker) + 'request_times.csv')

    service = service.replace('_', "-")
    print(pd.DataFrame(execution_time) / 1000)
    return (pd.DataFrame(execution_time) / 1000).T[service].mean()


def get_delay3(service, frequency, time_len, ):
    try:
        print(application_url + ':9411/api/v2/traces?limit=300&lookback=' + str(time_len))
        r = requests.get(
            application_url + ':9411/api/v2/traces?limit=300&lookback=' + str(time_len))
        print(r.status_code)
        r.raise_for_status()
    except Exception as e:
        print(e)

    # service + str(frequency) + '_delay.csv'
    pickle_file_name = measure_path + service + str(frequency) + '_json.pkl'
    with open(pickle_file_name, 'wb') as f:
        pickle.dump(r.json(), f)
    dfs = []
    for item in r.json():  # ['traceId'] # the trace id
        dfs.append(pd.DataFrame(item))

    services_call_time = {}
    execution_time = {}
    trace_request_time = {}
    trace_id = 0
    for dff in dfs:  
        if len(dff) == 1: 
            continue
        time_list = {}  # for record all services time
        for index, value in dff.iterrows():  
            if trace_id not in trace_request_time:
                trace_request_time[trace_id] = value['duration']
            else:
                trace_request_time[trace_id] = max(value['duration'],
                                                   trace_request_time[trace_id]) 

            if value['kind'] == 'SERVER':
                name = value['localEndpoint']['serviceName']
                if name not in time_list:
                    time_list[name] = []
                    time_list[name].append(value['duration'])
                else:
                    time_list[name].append(value['duration'])
        if len(time_list) == 0:
            continue
        services_call_time[trace_id] = {}
        execution_time[trace_id] = {}
        for key in time_list:
            short_key = key[3:-8]
            services_call_time[trace_id][short_key] = len(time_list[key])
            execution_time[trace_id][short_key] = np.mean(time_list[key])
        trace_id += 1

    pd.DataFrame(services_call_time).round(
        2).T.to_csv(measure_path + service + str(frequency) + '_call_times.csv')
    (pd.DataFrame(execution_time) / 1000).T.to_csv(measure_path + service + str(frequency) + '_delay.csv')
    (pd.DataFrame(trace_request_time, index=[
        'value']) / 1000).round(2).T.to_csv(measure_path + service + str(frequency) + 'request_times.csv')


def remove_from_parent(parent_span, child_span):
    parent_times = []
    for ts in parent_span['time']:
        start = ts[0]
        end = ts[1]
        if child_span['time'][0][0] < end and child_span['time'][0][1] > start:
            join = min(end, child_span['time'][0][1]) - max(start, child_span['time'][0][0])
            parent_span['duration'] -= join
            if parent_span['duration'] < 0:
                print(parent_span['duration'])
            sums = 0
            if start < child_span['time'][0][0]:
                parent_times.append([min(start, child_span['time'][0][0]), max(start, child_span['time'][0][0])])
                sums += (max(start, child_span['time'][0][0]) - min(start, child_span['time'][0][0]))
            if end > child_span['time'][0][1]:
                parent_times.append([min(end, child_span['time'][0][1]), max(end, child_span['time'][0][1])])
                sums += (max(end, child_span['time'][0][1]) - min(end, child_span['time'][0][1]))
            if end - start != sums + join:
                print('false', end - start, sums, join)
                print(child_span['time'][0], ts)
        else:
            parent_times.append([start, end])
    parent_span['time'] = parent_times
    return parent_span


def runtime_graph(data):
    execution_time = defaultdict(list)
    services_call_time = defaultdict(list)
    trace_request_time = {'value': []}
    for trace in data['data']:
        # build graph for each trace
        span_graph = {}
        processes = trace['processes']
        parent_list = []
        max_duration = 0
        for span in trace['spans']:
            if span['warnings'] is not None:
                print(span['warnings'])
                # continue
            spanID = span['spanID']
            parent = None
            if len(span['references']) > 0 and span['references'][0]['refType'] == 'CHILD_OF':
                parent = span['references'][0]['spanID']
            service = processes[span['processID']]['serviceName']
            duration = span['duration']
            max_duration = duration if duration > max_duration else max_duration
            start_time = span['startTime']
            if spanID not in span_graph:
                span_graph[spanID] = {'parent': parent, 'service': service, 'duration': duration,
                                      'time': [[start_time, start_time + duration]]}
                parent_list.append(parent)
            else:
                print('wrong')
        # subtract child running time
        trace_request_time['value'].append(max_duration)
        for key, value in sorted(span_graph.items(), key=lambda x: x[1]['duration'], reverse=True):
            # for key in span_graph.keys():
            parent, duration = span_graph[key]['parent'], span_graph[key]['duration']
            if parent is not None and parent in span_graph:
                span_graph[parent] = remove_from_parent(span_graph[parent], span_graph[key])
        # collect time for a service
        service_time = defaultdict(int)
        service_count = defaultdict(int)
        for key in span_graph.keys():
            service, duration = span_graph[key]['service'], span_graph[key]['duration']
            service_time[service] += duration
            service_count[service] += 1
        # save to global duration
        for key in social_services:
            if service_count[key+'-service'] == 0:
                execution_time[key].append(service_time[key+'-service'])
            else:
                execution_time[key].append(service_time[key+'-service'] / service_count[key+'-service'])
            services_call_time[key].append(service_count[key+'-service'])
    return services_call_time, execution_time, trace_request_time


def get_delay_jaeger(service, frequency, req_type, workers, time_len):
    service_name = service 
    time_len = int(time_len / 1000) 
    second = 1000000
    end = int(time.time() * second)
    start = end - second * time_len
    url = '{}:16686/api/traces?end={}&lookback=custom&limit=3000&start={}&service={}-service&prettyPrint=true'.format(
        application_url_social, end, start, service_name)
    print(url)
    r = requests.get(url)
    print('response code', r.status_code)
    if len(r.json()['data']) == 0:
        raise Exception('no response')
    pickle_file_name = measure_path_social + service + str(frequency) + req_type + str(workers) + '_json.pkl'
    with open(pickle_file_name, 'wb') as f:
        pickle.dump(r.json(), f)
    services_call_time, execution_time, trace_request_time = runtime_graph(r.json())
    pd.DataFrame(services_call_time).round(
        2).T.to_csv(measure_path_social + service + str(frequency) + req_type + str(workers) + '_call_times.csv')
    (pd.DataFrame(execution_time) / 1000).to_csv(
        measure_path_social + service + str(frequency) + req_type + str(workers) + '_delay.csv')
    (pd.DataFrame(trace_request_time) / 1000).round(2).T.to_csv(
        measure_path_social + service + str(frequency) + req_type + str(workers) + 'request_times.csv')
    # return sum(execution_time[service+'-service']) / len(execution_time[service+'-service'])
    # take care this will be na
    return (pd.DataFrame(execution_time).replace(0, np.NaN) / 1000)[service].mean()


if __name__ == '__main__':
    # get_delay('order_other', 2200000, 660000)
    data = get_delay_jaeger(60 * 5)
