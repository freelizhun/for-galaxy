FROM galaxy/galaxy-k8s:20.05 
RUN mkdir -p tools/mytools
COPY ./test-lammps-in-k8s.py tools/mytools
COPY ./test-vmd-in-k8s.py tools/mytools
COPY ./toolExample-lammpstest-in-k8s.xml tools/mytools  
COPY ./toolExample-vmdtest-in-k8s.xml tools/mytools
COPY ./dependency_resolvers_conf.xml config/
RUN pip install kubernetes -i https://pypi.tuna.tsinghua.edu.cn/simple/
