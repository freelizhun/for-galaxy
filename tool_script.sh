cat tool_script.sh 
#!/bin/bash

# The following block can be used by the job system
# to ensure this script is runnable before actually attempting
# to run it.
if [ -n "$ABC_TEST_JOB_SCRIPT_INTEGRITY_XYZ" ]; then
    exit 42
fi
/galaxy/server/.venv/bin/python '/galaxy/server/database/tools/mytools/test-lammps-in-k8s.py' '/galaxy/server/database/objects/3/a/0/dataset_3a011658-f92d-4331-a0fd-68f2f9a67681.dat' '/galaxy/server/database/objects/9/4/2/dataset_9
429f901-f389-4693-97a3-fca89ff4251c.dat' '/galaxy/server/database/objects/9/f/a/dataset_9fae5450-800a-488c-af34-c80375d3428e.dat'