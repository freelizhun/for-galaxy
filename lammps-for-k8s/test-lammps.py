from kubernetes import client, config
import time,re
import tarfile
from tempfile import TemporaryFile

from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

def exec_commands(api_instance,pod_name,namespace):
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
    # Begining to exec lammps command in lammps-deploy-*** pod
    exec_command = [
        '/bin/sh',
        '-c',
        'cd /test-data; source /etc/profile; mpirun -np 4 /home/test/lmp_mpi -in /home/test/in.lj']
    resp = stream(api_instance.connect_get_namespaced_pod_exec,
                  name,
                  exec_namespace,
                  command=exec_command,
                  stderr=True, stdin=False,
                  stdout=True, tty=False)
    print("Response: " + resp)
    
    #Begining to cp files from galaxy-web-*** pod to ubuntu-desk-vmd-*** pod's / dir
    exec_command_forcp=["tar","xvf","-","-C","/"]
    resp_forcp=stream(api_instance.connect_get_namespaced_pod_exec,
                      'ubuntu-desk-vmd-d85d9478d-kg6xp',
                      exec_namespace,
                      command=exec_command_forcp,
                      stderr=True, stdin=True,
                      stdout=True, tty=False,
                      _preload_content=False)
    
    source_file = '/galaxy/server/hello.txt'
    dest_file='/root/Desktop/hello.txt'
    with TemporaryFile() as tar_buffer:
        with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
            tar.add(source_file,dest_file)
    
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
            # print("Running command... %s\n" % c)

                resp_forcp.write_stdin(c.decode())
            else:
                break
        resp_forcp.close()

def main():
    config.load_incluster_config()
    #config.load_kube_config()
    v1 = client.CoreV1Api()
    print("Listing pods with their names:")
    
    #get the name of lammps-deploy-*** pod
    namespace='galaxy2'
    ret=v1.list_namespaced_pod(namespace)
    for i in ret.items:
        #print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
        if re.match(r'lammps-deploy-*',i.metadata.name):
            pod_name=i.metadata.name
            print('the pod_name is %s' % pod_name)
            break
    
    #c = Configuration()
    #c.assert_hostname = False
    #Configuration.set_default(c)
    #core_v1 = core_v1_api.CoreV1Api()
    core_v1=client.CoreV1Api()
    exec_commands(core_v1,pod_name,namespace)
    
    

if __name__ == '__main__':
    main()
