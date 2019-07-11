freq=$1
for i in $(cat "../pointings_f$freq.txt" | cut -d '/' -f4 | grep '_' | sort | uniq); do echo  $i; uvcat vis=../201*/f"$freq"_sources/$i out=$i ; done

