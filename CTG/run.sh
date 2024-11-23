#!/bin/bash

prj=$1
file=$2
begin=$3
end=$4

/usr/bin/python3.7 python parse_impacted_dependency_lines.py --project $prj --file $file --begin $begin --end $end
/usr/bin/python3.7 python generate_jit_vul_triggering_commit_data.py --project $prj --file $file --begin $begin --end $end
/usr/bin/python3.7 python parser_cpg_data.py --project $prj --file $file
/usr/bin/python3.7 python generate_ctg_graph.py --project $prj --file $file
/usr/bin/python3.7 python Main_Trim_CTG.py --data "$file"_ctg.csv