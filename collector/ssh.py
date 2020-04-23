import time
import paramiko
from configs import servers_dict, server_setting_path, measure_path, server_setting_path_social, measure_path_social
import pickle


class SSH:
    def __init__(self):
        self.servers_dict = servers_dict

    def execute(self, name='', port=22, cmds=[], root=True):
        """
        This function is for execute some commands through ssh connections
        :param name: server name
        :param ip: IP address
        :param port: port number
        :param cmds: the list of command to be
        :param root: execute as root, default: True
        :return: the result after execute the commands
        """
        ip, passwd = self.servers_dict[name]['ip'], self.servers_dict[name]['passwd']
        s = paramiko.SSHClient()
        s.load_system_host_keys()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            s.connect(hostname=ip, port=int(port),
                      username=name, password=passwd)
        except:
            print('err: can not conn %s ,pls check %s and password of xx', (ip, ip))
            return False

        if root:
            ssh = s.invoke_shell()
            time.sleep(1)
            ssh.send('sudo su\n')
            buff = ''
            while not buff.endswith(': '):
                resp = ssh.recv(2048)
                buff += resp.decode('utf-8')
                # print('s0', buff)
            ssh.send(passwd)
            ssh.send('\n')
            buff = ''
            while not buff.endswith('# '):
                resp = ssh.recv(2048)
                buff += resp.decode('utf-8')
                # print('s1', buff)
            for cmd in cmds:
                print(cmd)
                ssh.send(cmd)
                ssh.send('\n')
                buff = ''
                time.sleep(1)
                # resp = ssh.recv(2048)
                # resp = ''
                while not buff.endswith('# '):
                    resp = ssh.recv(2048)
                    buff += resp.decode('utf-8')
                    print('s3', resp.decode('utf-8'))
            s.close()
            result = buff
        else:
            for cmd in cmds:
                _, stdout, _ = s.exec_command(cmd)
                result = stdout.read().decode('utf-8')
            s.close()

        return result

    def set_cpu(self, server, frequency, core_num=12):
        """
        this function set all the cpu to frequency and print the 1st frequency for sanity check
        params:
             server: server name
             frequency : the frequency to be set
             core_num : num of cores in this server
        """
        prefix = '/sys/devices/system/cpu/cpu'
        suffix_max = '/cpufreq/scaling_max_freq'
        suffix_min = '/cpufreq/scaling_min_freq'
        cmds = []

        for core_id in range(self.servers_dict[server]['core_num']):
            max_file = prefix + str(core_id) + suffix_max
            cmds.append('echo "' + str(frequency) + '" >> ' + max_file)

            min_file = prefix + str(core_id) + suffix_min
            cmds.append('echo "' + str(frequency) + '" >> ' + min_file)
            cmds.append('cp ' + min_file + ' ' + max_file)
        _ = self.execute(name=server, port=22, cmds=cmds)
        # get frequency for check
        check_file = prefix + '1' + suffix_max
        cmds = ['cat ' + check_file]
        result = self.execute(server, cmds=cmds, root=False)
        assert int(frequency) == int(result)
        return result

    def record_power(self, server, deploy, frequency, timeout):
        cmds = ['cd /home/hxf/microservice/power-result/',
                'timeout ' + str(timeout) +
                ' turbostat --debug -S -i 1 > turbo_out',
                'cp turbo_out turbo_out' + deploy + str(frequency), 'cat turbo_out']
        _ = self.execute(server, port=22, cmds=cmds)

    def read_power(self, server, service, frequency, timeout):
        # statement = "sudo sh -c 'timeout 5 turbostat --debug -S -i 2 > turbo_out'"
        cmds = ['cd /home/hxf/microservice/power-result/',
                'timeout ' + str(timeout) + ' turbostat --debug -S -i 1 > turbo_out',
                'cp turbo_out turbo_out' + service + str(frequency), 'cat turbo_out']
        result = self.execute(name=server, cmds=cmds)
        pickle_file_name = measure_path + service + str(frequency) + '_pow.pkl'
        with open(pickle_file_name, 'wb') as f:
            pickle.dump(result, f)
        return self.phrase_reusult01(result)

    def read_power_full(self, server, service, frequency, req, worker, timeout):
        # statement = "sudo sh -c 'timeout 5 turbostat --debug -S -i 2 > turbo_out'"
        cmds = ['cd /home/hxf/microservice/power-result/',
                'timeout ' + str(timeout) + ' turbostat --debug -S -i 1 > turbo_out',
                'cp turbo_out turbo_out' + service + str(frequency) + req + str(worker), 'cat turbo_out']
        result = self.execute(name=server, cmds=cmds)
        pickle_file_name = measure_path + service + str(frequency) + req + str(worker) + '_pow.pkl'
        with open(pickle_file_name, 'wb') as f:
            pickle.dump(result, f)
        return self.phrase_reusult01(result)

    def read__both_power(self, server1, server2, deploy, frequency, timeout):
        # statement = "sudo sh -c 'timeout 5 turbostat --debug -S -i 2 > turbo_out'"
        cmds = ['cd /home/hxf/microservice/power-result/', 'cat turbo_out' + deploy + str(frequency)]
        result1 = self.execute(server1, cmds=cmds)
        result2 = self.execute(server2, cmds=cmds)

        # pickle_file_name1 = measure_path+deploy + str(frequency) + '_pow1.pkl'
        # with open(pickle_file_name1, 'wb') as f:
        #     pickle.dump(result, f)

        # pickle_file_name2 = measure_path+deploy + str(frequency) + '_pow2.pkl'
        # with open(pickle_file_name2, 'wb') as f:
        #     pickle.dump(result, f)
        return self.phrase_reusult01(result1), self.phrase_reusult01(result2)

    def phrase_reusult01(self, result):
        lines = result.split('\r\n')
        p_list = []
        cutoff = 5
        for line in lines[2:-cutoff]:
            count = 0
            for cha in line.split(' '):
                if (len(cha) > 0):
                    count += 1
                    if (count == 16):
                        p_list.append(float(cha))
                        break
            print('count=', count)
        return sum(p_list) / len(p_list)

    def phrase_reusult04(self, result):
        lines = result.split('\r\n')
        p_list = []
        for line in lines[2:-1]:
            count = 0
            for cha in line.split(' '):
                if len(cha) > 0:
                    count += 1
                    if count == 12:
                        p_list.append(float(cha))
                        break
            print(count)
        return sum(p_list) / len(p_list)

    def change_docker_train(self, server, deploy):
        """
        for change and deploy a new service
        :param service or deploy algorithm to be run.
        """
        while True:
            cmds = ['cp ' + server_setting_path + 'docker-compose-swarm-' + deploy
                    + '.yml ' + server_setting_path + 'docker-compose-swarm.yml']
            cmds.append('docker stack rm train-ticket-swarm')
            cmds.append('timeout 60 top')
            cmds.append('cd ' + server_setting_path)
            cmds.append(
                'docker stack deploy --compose-file=docker-compose-swarm.yml --orchestrator=swarm train-ticket-swarm')
            cmds.append('docker stack services train-ticket-swarm')
            result = self.execute(server, cmds=cmds)
            if 'Nothing found in stack: train-ticket-swarm' in result:
                print('\n\n service cannot up up up \n\n\n')
                continue
            else:
                break
        return result

    def close_train(self, server):
        """
        for change and deploy a new service
        """
        while True:
            cmds = []
            cmds.append('docker stack rm train-ticket-swarm')
            cmds.append('timeout 60 top')
            result = self.execute(server, cmds=cmds)
            if 'Nothing found in stack: train-ticket-swarm' in result:
                break
            else:
                continue
        return result

    def change_docker_social(self, server, deploy):
        """
        for change and deploy a new service
        """
        while True:
            cmds = ['cp ' + server_setting_path_social + 'docker-compose-swarm-' + deploy
                    + '.yml ' + server_setting_path_social + 'docker-compose-swarm.yml']
            cmds.append('docker stack rm social-swarm')
            cmds.append('timeout 20 top')
            cmds.append('cd '+ server_setting_path_social)
            cmds.append(
                'docker stack deploy --compose-file=docker-compose-swarm.yml --orchestrator=swarm social-swarm')
            cmds.append('docker stack services social-swarm')
            result = self.execute(server, cmds=cmds)
            if 'Nothing found in stack: social-swarm' in result:
                print('\n\n service cannot up up up \n\n\n')
                continue
            else:
                break
        return result

    def read_power_full_social(self, server, service, frequency, req, worker, timeout):
        # statement = "sudo sh -c 'timeout 5 turbostat --debug -S -i 2 > turbo_out'"
        cmds = ['cd ./power-result/',
                'timeout ' + str(timeout) + ' turbostat --debug -S -i 1 > turbo_out',
                'cp turbo_out turbo_out' + service + str(frequency) + req + str(worker), 'cat turbo_out']
        result = self.execute(name=server, cmds=cmds)
        pickle_file_name = measure_path_social + service + str(frequency) + req + str(worker) + '_pow.pkl'
        with open(pickle_file_name, 'wb') as f:
            pickle.dump(result, f)
        return self.phrase_reusult04(result)

    def close_social(self):
        pass
