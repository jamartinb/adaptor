#!/bin/bash


## ICSOC'11 and FACS'11 evaluation example
DIR="$HOME/workspace/itaca/samples/adaptor/ecows11"; 
CONTRACT="contract-5.xml";
SERVICES="SPIN_sink.xml SPIN_source.xml tiny_diffusion.xml";
LIMIT="";

## COORDINATION'11 and ECOWS'11 example
#DIR="$HOME/workspace/itaca/samples/adaptor/coordination11"; 
#CONTRACT="contract.xml";
#SERVICES="client.xml server.xml db.xml";
#LIMIT="";

## ICSE'09 example
#DIR="$HOME/workspace/itaca/samples/adaptor/med-online_renamed_session-aware";
#CONTRACT="contract.xml";
#SERVICES="client.xml server.xml db.xml";
#LIMIT="-l 19";

DEST="new_stats";

DTER="[0, 0, 0, 0, .0001, .0001, .001, .001, .001, .001, .01, .01, .1, .1, .001, .001, .0001, .0001, 0, 0]";
TIMES=1000;
SAMPLES=10;
THRESHOLDS="0";


EXAMPLE=$(basename "$DIR");

mkdir -p "$DEST"

SS="";

for SERV in $SERVICES
do
    SS="$SS ${DIR}/${SERV}"
done

echo $SS


python2.7 adaptor.py -c ${DIR}/${CONTRACT} $SS --dter "$DTER" -n ${SAMPLES} -s ${DEST}/stats_${EXAMPLE}_dter_reg_t${TIMES}_i20_n${SAMPLES}.txt --times ${TIMES} $LIMIT &&
python2.7 adaptor.py -c ${DIR}/${CONTRACT} $SS --ter .001 -i 20 -n ${SAMPLES} -s ${DEST}/stats_${EXAMPLE}_ter1e-3_reg_t${TIMES}_i20_n${SAMPLES}.txt --times ${TIMES} $LIMIT &&
python2.7 adaptor.py -c ${DIR}/${CONTRACT} $SS --ter .01 -i 20 -n ${SAMPLES} -s ${DEST}/stats_${EXAMPLE}_ter1e-2_reg_t${TIMES}_i20_n${SAMPLES}.txt --times ${TIMES} $LIMIT &&
python2.7 adaptor.py -c ${DIR}/${CONTRACT} $SS --ter .1 -i 20 -n ${SAMPLES} -s ${DEST}/stats_${EXAMPLE}_ter1e-1_reg_t${TIMES}_i20_n${SAMPLES}.txt --times ${TIMES} $LIMIT &&
python2.7 adaptor.py -c ${DIR}/${CONTRACT} $SS -i 20 -n ${SAMPLES} -s ${DEST}/stats_${EXAMPLE}_ter0_reg_t${TIMES}_i20_n${SAMPLES}.txt --times ${TIMES} $LIMIT


for adaptor in sthr dthr athr
do
    for threshold in $THRESHOLDS
    do
        if [ $? -ne 0 ]
        then
            exit $?;
        fi
        arg="--$adaptor $threshold";
        abv="${adaptor}${threshold}";
        python2.7 adaptor.py -c ${DIR}/${CONTRACT} $SS --dter "$DTER" $arg -n ${SAMPLES} -s ${DEST}/stats_${EXAMPLE}_dter_${abv}_t${TIMES}_i20_n${SAMPLES}.txt --times ${TIMES} $LIMIT &&
        python2.7 adaptor.py -c ${DIR}/${CONTRACT} $SS --ter .001 $arg -i 20 -n ${SAMPLES} -s ${DEST}/stats_${EXAMPLE}_ter1e-3_${abv}_t${TIMES}_i20_n${SAMPLES}.txt --times ${TIMES} $LIMIT &&
        python2.7 adaptor.py -c ${DIR}/${CONTRACT} $SS --ter .01 $arg -i 20 -n ${SAMPLES} -s ${DEST}/stats_${EXAMPLE}_ter1e-2_${abv}_t${TIMES}_i20_n${SAMPLES}.txt --times ${TIMES} $LIMIT &&
        python2.7 adaptor.py -c ${DIR}/${CONTRACT} $SS --ter .1 $arg -i 20 -n ${SAMPLES} -s ${DEST}/stats_${EXAMPLE}_ter1e-1_${abv}_t${TIMES}_i20_n${SAMPLES}.txt --times ${TIMES} $LIMIT &&
        python2.7 adaptor.py -c ${DIR}/${CONTRACT} $SS $arg -i 20 -n ${SAMPLES} -s ${DEST}/stats_${EXAMPLE}_ter0_${abv}_t${TIMES}_i20_n${SAMPLES}.txt --times ${TIMES} $LIMIT
    done
done

python2.7 plot_stats.py ${DEST}/stats_${EXAMPLE}_dter_dthr0_t${TIMES}_i20_n10.txt ${DEST}/stats_${EXAMPLE}_dter_sthr0_t${TIMES}_i20_n10.txt ${DEST}/stats_${EXAMPLE}_dter_reg_t${TIMES}_i20_n10.txt ${DEST}/stats_${EXAMPLE}_dter_athr0_t${TIMES}_i20_n10.txt -m ${TIMES}

python2.7 plot_stats.py ${DEST}/stats_${EXAMPLE}_dter_dthr0_t${TIMES}_i20_n10.txt ${DEST}/stats_${EXAMPLE}_dter_sthr0_t${TIMES}_i20_n10.txt ${DEST}/stats_${EXAMPLE}_dter_reg_t${TIMES}_i20_n10.txt ${DEST}/stats_${EXAMPLE}_dter_athr0_t${TIMES}_i20_n10.txt -m ${TIMES} -b ${DEST}/stats_${EXAMPLE}_dter_sthr0_t${TIMES}_i20_n10.txt
