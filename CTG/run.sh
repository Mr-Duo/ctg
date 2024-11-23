#!/bin/bash

prj=$1
file=$2
begin=$3
end=$4

python parse_impacted_dependency_lines.py --project $prj --file $file --begin $begin --end $end
python generate_jit_vul_triggering_commit_data.py --project $prj --file $file --begin $begin --end $end
python parser_cpg_data.py --project $prj --file $file
python generate_ctg_graph.py --project $prj --file $file
python Main_Trim_CTG.py --data "$file"_ctg.csv