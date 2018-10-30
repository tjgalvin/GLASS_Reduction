for i in $(cat pointings.txt | grep '_' | sort | uniq); do echo $i; echo uvcat in=201*/f9500/$i.9500 out=Pointings_f9500/$i.9500; done

