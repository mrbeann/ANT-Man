# coding=utf-8
from collector.ssh import SSH
from configs import deploy_list, frequency_list, measure_path, service_dict, focus_server, other_server, \
    request_sender_url
import pickle
import os
import time
from concurrent.futures import ProcessPoolExecutor
import requests
from collector import delay


def collect_service_model(request_type='train-advanced'):
    """
    :param request_type:
    :return:
    """
    power_qos = {}
    ssh = SSH()
    for service in service_dict[request_type]:
        power_qos[service] = {}
        # all file in this services is done.
        pickle_file_name = measure_path + service + str(frequency_list[-1]) + '.pkl'
        if os.path.exists(pickle_file_name):
            print('read', pickle_file_name)
            with open(pickle_file_name, 'rb') as f:
                power_qos = pickle.load(f)
            continue

        # this service is properly set
        pickle_file_name = measure_path + service + str(frequency_list[0]) + '.pkl'
        if os.path.exists(pickle_file_name):
            print('read', pickle_file_name)
            with open(pickle_file_name, 'rb') as f:
                power_qos = pickle.load(f)
        else:
            ssh.change_docker_train(other_server, service)  # deploy dockers
            time.sleep(90)

        for frequency in frequency_list:
            pickle_file_name = measure_path + service + str(frequency) + '.pkl'
            if os.path.exists(pickle_file_name):
                print('read', pickle_file_name)
                with open(pickle_file_name, 'rb') as f:
                    power_qos = pickle.load(f)
                continue
            retry = 0
            while True:
                assert retry < 3
                try:
                    start = time.time()
                    ssh.set_cpu(focus_server, frequency, core_num=None)
                    # request and get power
                    workers = 30
                    send_done = 1
                    while send_done > 0:
                        try:
                            requests.get(
                                request_sender_url + 'basicworkers/' + str(workers))
                            send_done = 0
                        except:
                            time.sleep(60 * send_done)
                            continue
                    time.sleep(10)
                    avg_pow = ssh.read_power(focus_server, service, frequency, timeout=int(
                        500 / int(workers)) + 30)  # timeout in seconds
                    time_len = int((time.time() - start) * 1000) + 6000
                    avg_delay = delay.get_delay(service, frequency, time_len)
                    print('get delay')
                    power_qos[service][frequency] = {
                        'pow': avg_pow, 'delay': avg_delay}
                    time.sleep(60)
                    pickle_file_name = measure_path + service + str(frequency) + '.pkl'
                    with open(pickle_file_name, 'wb') as f:
                        pickle.dump(power_qos, f)
                    retry = 0
                    break
                except Exception as e:
                    print('\n\n\n\n\n\n\n\n\n', retry, repr(e), '\n\n\n\n\n\n')
                    retry += 1
                    continue


def collect_deploy_model():
    ssh = SSH()
    power_qos = {}
    for deploy in deploy_list:
        power_qos[deploy] = {}
        # all file in this services is done.
        pickle_file_name = measure_path + deploy + str(frequency_list[-1]) + '.pkl'
        if os.path.exists(pickle_file_name):
            print('read', pickle_file_name)
            with open(pickle_file_name, 'rb') as f:
                power_qos = pickle.load(f)
            continue

        # this service is properly set
        pickle_file_name = measure_path + deploy + str(frequency_list[0]) + '.pkl'
        if os.path.exists(pickle_file_name):
            print('read', pickle_file_name)
            with open(pickle_file_name, 'rb') as f:
                power_qos = pickle.load(f)
        else:
            ssh.change_docker_train(other_server, deploy)  # deploy dockers
            time.sleep(90)

        for frequency in frequency_list:
            pickle_file_name = measure_path + deploy + str(frequency) + '.pkl'
            if os.path.exists(pickle_file_name):
                print('read', pickle_file_name)
                with open(pickle_file_name, 'rb') as f:
                    power_qos = pickle.load(f)
                continue
            retry = 0
            while True:
                assert retry < 3
                try:
                    start = time.time()
                    ssh.set_cpu(focus_server, frequency, core_num=12)
                    if deploy == 'capping':
                        ssh.set_cpu(other_server, frequency, core_num=12)
                    else:
                        ssh.set_cpu(other_server, 2400000, core_num=12)
                    # request and get power
                    workers = 25
                    send_done = 1
                    while send_done > 0:
                        try:
                            requests.get(
                                request_sender_url + 'mixeddworkers/' + str(workers))
                            send_done = 0
                        except:
                            time.sleep(60 * send_done)
                            continue
                    time.sleep(10)
                    executor = ProcessPoolExecutor(max_workers=2)
                    executor.submit(ssh.record_power, focus_server, deploy, frequency, timeout=int(
                        500 / int(workers)) + 30)
                    executor.submit(ssh.record_power, other_server, deploy, frequency, timeout=int(
                        500 / int(workers)) + 30)
                    executor.shutdown(wait=True)
                    avg_pow1, avg_pow2 = ssh.read_both_power(focus_server, other_server, deploy, frequency, 60)

                    time_len = int((time.time() - start) * 1000) + 6000
                    delay.get_delay(deploy, frequency, time_len)
                    print('delay done!')
                    power_qos[deploy][frequency] = {
                        'pow1': avg_pow1, 'power2': avg_pow2}
                    time.sleep(60)
                    pickle_file_name = measure_path + deploy + str(frequency) + '.pkl'
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
            collect_service_model()
            break
        except Exception as e:
            print('errors', repr(e))
