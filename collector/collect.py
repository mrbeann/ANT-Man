# coding=utf-8
from collector.ssh import SSH
from configs import frequency_list, measure_path, service_dict, focus_server, other_server, request_sender_url, loads, \
    request_types, train_exe_time
import pickle
import os
import time
import requests
from collector import delay


def collect_diff_full(request_type='train-advanced'):
    """
    :param request_type:
    :return:
    """
    power_qos = {}
    ssh = SSH()
    for service in service_dict[request_type]:
        power_qos[service] = {}
        # all file in this services is done.
        pickle_file_name = measure_path + service + str(frequency_list[-1]) + str(request_types[-1]) + str(
            loads[-1]) + '.pkl'
        if os.path.exists(pickle_file_name):
            print('read', pickle_file_name)
            with open(pickle_file_name, 'rb') as f:
                power_qos = pickle.load(f)
            continue

        # this service is properly set
        pickle_file_name = measure_path + service + str(frequency_list[0]) + str(request_types[0]) + str(
            loads[0]) + '.pkl'
        if os.path.exists(pickle_file_name):
            print('read', pickle_file_name)
            with open(pickle_file_name, 'rb') as f:
                power_qos = pickle.load(f)
        else:
            ssh.change_docker_train(other_server, service)  # deploy dockers
            time.sleep(45)

        for frequency in frequency_list:
            pickle_file_name = measure_path + service + str(frequency) + str(request_types[-1]) + str(
                loads[-1]) + '.pkl'
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
                    ssh.set_cpu(focus_server, frequency, core_num=12)
                    # request and get power
                    for req_type in request_types:
                        if req_type == 'basicworkers' and service not in service_dict['train-basic']:
                            continue
                        power_qos[service][frequency][req_type] = {}
                        for workers in loads:
                            send_done = 1
                            while send_done > 0:
                                try:
                                    start = time.time()
                                    requests.get(request_sender_url + req_type + '/' + str(workers))
                                    send_done = 0
                                except:
                                    time.sleep(60 * send_done)
                                    continue
                            time.sleep(10)
                            timeout = train_exe_time[req_type][workers]
                            avg_pow = ssh.read_power_full(focus_server, service, frequency, req_type, workers,
                                                          timeout=timeout) 
                            time_len = int((time.time() - start) * 1000) + 3000
                            avg_delay = delay.get_delay2_full(service, frequency, req_type, workers, time_len)
                            print('get delay')
                            power_qos[service][frequency][req_type][str(workers)] = {'pow': avg_pow, 'delay': avg_delay}
                            time.sleep(15)
                            pickle_file_name = measure_path + service + str(frequency) + str(req_type) + str(workers) + '.pkl'
                            with open(pickle_file_name, 'wb') as f:
                                pickle.dump(power_qos, f)
                            retry = 0
                    break
                except Exception as e:
                    print('\n\n\n\n\n\n\n\n\n', retry, repr(e), '\n\n\n\n\n\n')
                    retry += 1
                    continue


if __name__ == "__main__":
    # ssh = SSH()
    # assert ssh.execute(cmds=['ls']) is not False
    # ssh.change_docker(server='sail01', deploy='PC')
    while True:
        try:
            collect_diff_full()
            break
        except Exception as e:
            print('errors', repr(e))
