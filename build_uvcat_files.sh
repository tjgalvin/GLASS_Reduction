freq=$1
for i in $(cat pointings.txt | grep '_' | sort | uniq); do echo  $i; uvcat vis=201*/f$freq/$i.$freq out=Pointings_f$freq/$i.$freq; done

