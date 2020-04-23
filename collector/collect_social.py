# coding=utf-8
"""
data collector for social network
"""
from collector.ssh import SSH
from configs import frequency_list, measure_path_social, service_dict, focus_server_social, other_server_social, \
    request_sender_url_social, social_services, request_types_social, loads_social
import pickle
import os
import time
import requests
from collector import delay


def collect_service_model():
    power_qos = {}
    ssh = SSH()
    for service in social_services:
        power_qos[service] = {}
        # all file in this services is done.
        for req_t in request_types_social[::-1]:
            if service in service_dict[req_t]:
                break

        pickle_file_name = measure_path_social + service + str(frequency_list[-1]) + str(
            req_t) + str(loads_social[-1]) + '.pkl'
        if os.path.exists(pickle_file_name):
            print('all service ', service, 'done read', pickle_file_name)
            with open(pickle_file_name, 'rb') as f:
                power_qos = pickle.load(f)
            continue

        # this service is properly set
        for req_t in request_types_social:
            if service in service_dict[req_t]:
                break
        pickle_file_name = measure_path_social + service + str(frequency_list[0]) + str(req_t) + str(
            loads_social[0]) + '.pkl'
        if os.path.exists(pickle_file_name):
            print('read', pickle_file_name)
            with open(pickle_file_name, 'rb') as f:
                power_qos = pickle.load(f)
        else:
            ssh.change_docker_social(other_server_social, service)  # deploy dockers
            time.sleep(30)

        for frequency in frequency_list:
            for req_t in request_types_social[::-1]:
                if service in service_dict[req_t]:
                    break
            pickle_file_name = measure_path_social + service + str(frequency) + str(req_t) + str(
                loads_social[-1]) + '.pkl'
            if os.path.exists(pickle_file_name):
                print('read', pickle_file_name)
                with open(pickle_file_name, 'rb') as f:
                    power_qos = pickle.load(f)
                continue
            else:
                power_qos[service][frequency] = {}
            retry = 0
            while True:
                assert retry < 3
                try:
                    ssh.set_cpu(focus_server_social, frequency, core_num=None)
                    # request and get power
                    for req_type in request_types_social:
                        if service not in service_dict[req_type]:
                            print('skip', service, req_type)
                            continue
                        power_qos[service][frequency][req_type] = {}
                        for workers in loads_social:
                            send_done = 1
                            while send_done > 0:
                                try:
                                    start = time.time()
                                    requests.get(request_sender_url_social + req_type + '/' + str(workers))
                                    send_done = 0
                                except:
                                    time.sleep(30 * send_done)
                                    continue
                            timeout = 15
                            avg_pow = ssh.read_power_full_social(focus_server_social, service, frequency, req_type,
                                                                 workers, timeout=timeout)
                            time_len = int((time.time() - start) * 1000) + 15000
                            avg_delay = delay.get_delay_jaeger(service, frequency, req_type, workers, time_len)
                            print(avg_delay)
                            print('get delay')
                            power_qos[service][frequency][req_type][str(workers)] = {'pow': avg_pow, 'delay': avg_delay}
                            time.sleep(15)
                            pickle_file_name = measure_path_social + service + str(frequency) + str(req_type) + str(
                                workers) + '.pkl'
                            with open(pickle_file_name, 'wb') as f:
                                pickle.dump(power_qos, f)
                            retry = 0
                    break
                except Exception as e:
                    print('\n\n\n\n\n\n\n\n\n', retry, repr(e), '\n\n\n\n\n\n')
                    retry += 1
                    if retry > 1:
                        ssh.change_docker_social(other_server_social, service)  # deploy dockers
                        time.sleep(30)
                    continue


if __name__ == "__main__":
    # ssh = SSH()
    # assert ssh.execute(cmds=['ls']) is not False
    # ssh.change_docker(server='sail01', deploy='PC')
    while True:
        try:
            collect_service_model()
            break
        except Exception as e:
            print('errors', repr(e))
