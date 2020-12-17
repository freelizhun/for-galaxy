from kubernetes import client, config
import time, re, os, sys
import tarfile
from tempfile import TemporaryFile

from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

#kubernetes 12.0.1
def exec_commands(api_instance,pod_name,namespace,input_file_name):
    name = pod_name
    exec_namespace=namespace
    input_file_name=input_file_name
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

    # Begining to exec cmd in lammps-pod
    cmd='cd /test-data; source /etc/profile; mpirun -np 4 /home/test/lmp_mpi -in /test-data/%s' % input_file_name
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
    if not os.path.exists('/galaxy/server/data-cache'):
        os.makedirs('/galaxy/server/data-cache')
    #获取tools的.xml配置文件中的输入输出参数
    input_file_galaxy = sys.argv[1]
    input_file_name = 'in.test'
    input_file_dir_name = os.path.join('/galaxy/server/data-cache', input_file_name)
    output_file_galaxy = sys.argv[2]
    output_file_name='dump.melt'
    output_filename_dir_name=os.path.join('/galaxy/server/data-cache',output_file_name)
    log_filename_galaxy = sys.argv[3]
    log_filename = 'log.lammps'
    log_filename_dir_name = os.path.join('/galaxy/server/data-cache',log_filename)

    #在galaxy pod中的/galaxy/server/data-cache目录统一存放输入文件
    with open(input_file_galaxy, 'r') as fread:
        for line in fread:
            with open(input_file_dir_name, "a") as fwrite:
                fwrite.write(line)


    #集群内部即pod内使用，加载config配置文件
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    print("Listing pods with their names:")
    
    #匹配找到lammps-deploy这个pod的名字
    namespace='galaxy2'
    ret=v1.list_namespaced_pod(namespace)
    for i in ret.items:
        #print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
        if re.match(r'lammps-deploy-*',i.metadata.name):
            pod_name=i.metadata.name
            print('the pod_name is %s' % pod_name)
            break

    core_v1=client.CoreV1Api()
    #开始在pod即lammps-deploy-***中执行lammps数值模拟计算命令
    exec_commands(core_v1,pod_name,namespace,input_file_name)

    #开始将输出文件写入到output_file_galaxy = sys.argv[2]
    with open(output_filename_dir_name, 'r') as fread2:
        for line in fread2:
            with open(output_file_galaxy, 'a') as fwrite2:
                fwrite2.write(line)

    #开始将lammps日志文件输出到log_filename_galaxy = sys.argv[3]
    with open(log_filename_dir_name, 'r') as fread3:
        for line in fread3:
            with open(log_filename_galaxy, 'a') as fwrite3:
                fwrite3.write(line)
    

if __name__ == '__main__':
    main()
