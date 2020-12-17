from kubernetes import client, config
import time, re, os, sys
import tarfile
from tempfile import TemporaryFile

from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

#kubernetes 12.0.1
def exec_commands_cp(api_instance,pod_name,namespace,input_file_name):
    name = pod_name 
    exec_namespace=namespace
    resp = None
    try:
        resp = api_instance.read_namespaced_pod(name=name,
                                                namespace=exec_namespace)
    except ApiException as e:
        if e.status != 404:
            print("Unknown error: %s" % e)
            exit(1)

    if not resp:
        print("Pod %s does not exist. Please creating it..." % name)
        exit(1)

    # Begining to cp source_file from galaxy-web-*** pod to ubuntu-desk-vmd-*** pod's dest_file
    try:
        exec_command_forcp = ["tar", "xvf", "-", "-C", "/"]
        resp_forcp = stream(api_instance.connect_get_namespaced_pod_exec,
                        name,
                        exec_namespace,
                        command=exec_command_forcp,
                        stderr=True, stdin=True,
                        stdout=True, tty=False,
                        _preload_content=False)

        source_file = input_file_name
        dest_file = '/root/Desktop/dump.melt'
        with TemporaryFile() as tar_buffer:
            with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
                tar.add(source_file, dest_file)

            tar_buffer.seek(0)
            commands = []
            commands.append(tar_buffer.read())
            while resp_forcp.is_open():
                resp_forcp.update(timeout=1)
                if resp_forcp.peek_stdout():
                    print("STDOUT: %s" % resp_forcp.read_stdout())
                if resp_forcp.peek_stderr():
                    print("STDERR: %s" % resp_forcp.read_stderr())
                if commands:
                    c = commands.pop(0)
                    resp_forcp.write_stdin(c.decode())
                else:
                    break
            resp_forcp.close()
    except ApiException as e:
        print("Exception when copying files from galaxy-web-*** to ubuntu-desk-vmd-*** %s \n" % e)

def exec_commands_vmd(api_instance,pod_name,namespace):
    name = pod_name
    exec_namespace=namespace
    resp = None
    try:
        resp = api_instance.read_namespaced_pod(name=name,
                                                namespace=exec_namespace)
    except ApiException as e:
        if e.status != 404:
            print("Unknown error: %s" % e)
            exit(1)

    if not resp:
        print("Pod %s does not exist. Please creating it..." % name)
        exit(1)

    # Begining to exec cmd in vmd-pod
    cmd='vmd'
    exec_command = [
        '/bin/sh',
        '-c',cmd]
    resp = stream(api_instance.connect_get_namespaced_pod_exec,
                  name,
                  exec_namespace,
                  command=exec_command,
                  stderr=True, stdin=False,
                  stdout=True, tty=False)
    print("Response: " + resp)
def main():
    #获取tools的.xml配置文件中的输入输出参数
    input_file_galaxy = sys.argv[1]
    #input_file_name = 'dump.melt'
    current_path = os.path.abspath('.')
    #input_file_dir_name = os.path.join(current_path, input_file_name)
    output_file_galaxy = sys.argv[2]
    output_file_name='log.txt'
    output_filename_dir_name=os.path.join(current_path,output_file_name)

    #with open(input_file_galaxy, 'r') as fread:
    #    for line in fread:
    #        with open(input_file_dir_name, "a") as fwrite:
    #            fwrite.write(line)

    #集群内部即pod内使用，加载config配置文件
    config.load_incluster_config()
    namespace='galaxy2'
    pod_name='ubuntu-desk-vmd-7989c5946d-fqsr8'
    core_v1=client.CoreV1Api()
    #开始在pod即galaxy-web-***中执行cp文件到ubuntu-desk-vm-***的命令
    exec_commands_cp(core_v1,pod_name,namespace,input_file_galaxy)
    
    #开始在pod即ubuntu-desk-vm-***中执行vmd命令打开vmd可视化软件
    #exec_commands_vmd(core_v1,pod_name,namespace)
    
    cmd_for_log1=r'echo "Please to visit http://192.168.108.109:30008 to use vmd for visualization">>log.txt'
    os.system(cmd_for_log1)
    cmd_for_log2=r'echo "Then click the icon in the lower left corner:">>log.txt'
    os.system(cmd_for_log2)
    cmd_for_log3=r'echo "-> System Tools">>log.txt'
    os.system(cmd_for_log3)
    cmd_for_log4=r'echo "-> LXTerminal">>log.txt'
    os.system(cmd_for_log4)
    cmd_for_log5=r'echo "$ cd Desktop">>log.txt'
    os.system(cmd_for_log5)
    cmd_for_log6=r'echo "$ vmd">>log.txt'
    os.system(cmd_for_log6)
    #开始将输出文件写入到output_file_galaxy = sys.argv[2]
    with open(output_filename_dir_name, 'r') as fread2:
        for line in fread2:
            with open(output_file_galaxy, 'a') as fwrite2:
                fwrite2.write(line)

if __name__ == '__main__':
    main()
