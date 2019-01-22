freq=$1
for i in $(cat "../pointings_f$freq.txt" | cut -d '/' -f4 | grep '_' | sort | uniq); do echo  $i; uvcat vis=201*/f$freq/$i out=Pointings_f$freq/$i ; done

