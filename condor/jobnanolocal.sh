#!/bin/sh
set -x

PROCID=`cat .job.ad | grep 'ProcId' | awk '{print $3}'`

if [ "$PROCID" == 0 ]
then
  exit 0
fi

OUTDIR=/storage/user/jbalcas/NANO_PERF/LOCAL/
mkdir -p $OUTDIR

OUTEXISTS=`ls $OUTDIR/jobrep-$PROCID-0 | wc -l`

if [ "$OUTEXISTS" != 0 ]
then
  ls $OUTDIR/jobrep-$PROCID-0
  exit 0
fi

source /cvmfs/cms.cern.ch/cmsset_default.sh
cmsrel CMSSW_10_2_3
cd CMSSW_10_2_3/src/
cmsenv
cp /storage/user/jbalcas/CMSSW_10_2_3/src/NANO2016MC.py pset-$PROCID.py

LFN=`head -$PROCID /storage/user/jbalcas/CMSSW_10_2_3/src/files | tail -1`
echo $PROCID $LFN
date +%s
cp /mnt/hadoop/$LFN .
date +%s
FILENAME=`basename $LFN`
PWD=`pwd`
FULLPATH=$PWD/$FILENAME

sed -i -e 's|INPUTFILE=|INPUTFILE="file://'"${FULLPATH}"'"|g' pset-$PROCID.py

cat pset-$PROCID.py

cmsRun -j myjobrep-$PROCID pset-$PROCID.py
exitcode=$?
cp myjobrep-$PROCID $OUTDIR/jobrep-$PROCID-$exitcode
exit $exitcode
