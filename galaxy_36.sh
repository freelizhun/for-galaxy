#!/bin/bash



_galaxy_setup_environment() {
    local _use_framework_galaxy="$1"
    _GALAXY_JOB_DIR="/galaxy/server/database/jobs_directory/000/36"
    _GALAXY_JOB_HOME_DIR="/galaxy/server/database/jobs_directory/000/36/home"
    _GALAXY_JOB_TMP_DIR=$([ ! -e '/galaxy/server/database/jobs_directory/000/36/tmp' ] || mv '/galaxy/server/database/jobs_directory/000/36/tmp' '/galaxy/server/database/jobs_directory/000/36'/tmp.$(date +%Y%m%d-%H%M%S) ; mkdir '/g
alaxy/server/database/jobs_directory/000/36/tmp'; echo '/galaxy/server/database/jobs_directory/000/36/tmp')

    if [ "$GALAXY_LIB" != "None" -a "$_use_framework_galaxy" = "True" ]; then
        if [ -n "$PYTHONPATH" ]; then
            PYTHONPATH="$GALAXY_LIB:$PYTHONPATH"
        else
            PYTHONPATH="$GALAXY_LIB"
        fi
        export PYTHONPATH
    fi
    # These don't get cleaned on a re-run but may in the future.
    [ -z "$_GALAXY_JOB_TMP_DIR" -a ! -f "$_GALAXY_JOB_TMP_DIR" ] || mkdir -p "$_GALAXY_JOB_TMP_DIR"
    [ -z "$_GALAXY_JOB_HOME_DIR" -a ! -f "$_GALAXY_JOB_HOME_DIR" ] || mkdir -p "$_GALAXY_JOB_HOME_DIR"
    if [ "$GALAXY_VIRTUAL_ENV" != "None" -a -f "$GALAXY_VIRTUAL_ENV/bin/activate" \
         -a "`command -v python`" != "$GALAXY_VIRTUAL_ENV/bin/python" ]; then
        . "$GALAXY_VIRTUAL_ENV/bin/activate"
    fi
}


# The following block can be used by the job system
# to ensure this script is runnable before actually attempting
# to run it.
if [ -n "$ABC_TEST_JOB_SCRIPT_INTEGRITY_XYZ" ]; then
    exit 42
fi

export GALAXY_SLOTS_CONFIGURED="1"
if [ -n "$SLURM_CPUS_ON_NODE" ]; then
    # This should be valid on SLURM except in the case that srun is used to
    # submit additional job steps under an existing allocation, which we do not
    # currently do.
    GALAXY_SLOTS="$SLURM_CPUS_ON_NODE"
elif [ -n "$SLURM_NTASKS" ] || [ -n "$SLURM_CPUS_PER_TASK" ]; then
    # $SLURM_CPUS_ON_NODE should be set correctly on SLURM (even on old
    # installations), but keep the $SLURM_NTASKS logic as a backup since this
    # was the previous method under SLURM.
    #
    # Multiply these values since SLURM_NTASKS is total tasks over all nodes.
    # GALAXY_SLOTS maps to CPUS on a single node and shouldn't be used for
    # multi-node requests.
    GALAXY_SLOTS=`expr "${SLURM_NTASKS:-1}" \* "${SLURM_CPUS_PER_TASK:-1}"`
elif [ -n "$NSLOTS" ]; then
    GALAXY_SLOTS="$NSLOTS"
elif [ -n "$NCPUS" ]; then
    GALAXY_SLOTS="$NCPUS"
elif [ -n "$PBS_NCPUS" ]; then
    GALAXY_SLOTS="$PBS_NCPUS"
elif [ -f "$PBS_NODEFILE" ]; then
    GALAXY_SLOTS=`wc -l < $PBS_NODEFILE`
elif [ -n "$LSB_DJOB_NUMPROC" ]; then
    GALAXY_SLOTS="$LSB_DJOB_NUMPROC"
elif [ -n "$GALAXY_SLOTS" ]; then
    # kubernetes runner injects GALAXY_SLOTS into environment
    GALAXY_SLOTS=$GALAXY_SLOTS
else
    GALAXY_SLOTS="1"
    unset GALAXY_SLOTS_CONFIGURED
fi

export GALAXY_SLOTS
GALAXY_VIRTUAL_ENV="None"
_GALAXY_VIRTUAL_ENV="None"
PRESERVE_GALAXY_ENVIRONMENT="False"
GALAXY_LIB="/galaxy/server/lib"
_galaxy_setup_environment "$PRESERVE_GALAXY_ENVIRONMENT"
GALAXY_PYTHON=`command -v python`
cd /galaxy/server/database/jobs_directory/000/36
if [ -n "$SLURM_JOB_ID" ]; then
    GALAXY_MEMORY_MB=`scontrol -do show job "$SLURM_JOB_ID" | sed 's/.*\( \|^\)Mem=\([0-9][0-9]*\)\( \|$\).*/\2/p;d'` 2>memory_statement.log
fi
if [ -n "$SGE_HGR_h_vmem" ]; then
    GALAXY_MEMORY_MB=`echo "$SGE_HGR_h_vmem" | sed 's/G$/ * 1024/' | bc | cut -d"." -f1` 2>memory_statement.log
fi

if [ -z "$GALAXY_MEMORY_MB_PER_SLOT" -a -n "$GALAXY_MEMORY_MB" ]; then
    GALAXY_MEMORY_MB_PER_SLOT=$(($GALAXY_MEMORY_MB / $GALAXY_SLOTS))
elif [ -z "$GALAXY_MEMORY_MB" -a -n "$GALAXY_MEMORY_MB_PER_SLOT" ]; then
    GALAXY_MEMORY_MB=$(($GALAXY_MEMORY_MB_PER_SLOT * $GALAXY_SLOTS))
fi
[ "${GALAXY_MEMORY_MB--1}" -gt 0 ] 2>>memory_statement.log && export GALAXY_MEMORY_MB || unset GALAXY_MEMORY_MB
[ "${GALAXY_MEMORY_MB_PER_SLOT--1}" -gt 0 ] 2>>memory_statement.log && export GALAXY_MEMORY_MB_PER_SLOT || unset GALAXY_MEMORY_MB_PER_SLOT

echo "$GALAXY_SLOTS" > '/galaxy/server/database/jobs_directory/000/36/__instrument_core_galaxy_slots'
echo "$GALAXY_MEMORY_MB" > '/galaxy/server/database/jobs_directory/000/36/__instrument_core_galaxy_memory_mb'
date +"%s" > /galaxy/server/database/jobs_directory/000/36/__instrument_core_epoch_start
out="${TMPDIR:-/tmp}/out.$$" err="${TMPDIR:-/tmp}/err.$$"
mkfifo "$out" "$err"
trap 'rm "$out" "$err"' EXIT
tee -a stdout.log < "$out" &
tee -a stderr.log < "$err" >&2 & mkdir -p working outputs configs
if [ -d _working ]; then
    rm -rf working/ outputs/ configs/; cp -R _working working; cp -R _outputs outputs; cp -R _configs configs
else
    cp -R working _working; cp -R outputs _outputs; cp -R configs _configs
fi
cd working; /bin/bash /galaxy/server/database/jobs_directory/000/36/tool_script.sh > ../outputs/tool_stdout 2> ../outputs/tool_stderr > '/galaxy/server/database/jobs_directory/000/36/galaxy_36.o' 2> '/galaxy/server/database/jobs_di
rectory/000/36/galaxy_36.e'; return_code=$?; sh -c "exit $return_code"
echo $? > /galaxy/server/database/jobs_directory/000/36/galaxy_36.ec
date +"%s" > /galaxy/server/database/jobs_directory/000/36/__instrument_core_epoch_end