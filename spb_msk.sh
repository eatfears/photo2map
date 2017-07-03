#!/bin/sh

IN=a2/
OUT=${IN}out/
OUT_MAP=${OUT}map/

COL_COR="-brightness-contrast 30x50"
GIF_PARAM="-resize 500 -delay 20 -loop 0"

# -f 17.885

for f in ${IN}*.jpg
do
	ONAME=$(echo `basename $f` |  grep -o  '[0-9]\+_[0-9]\+').png

	if [ ! -f ${OUT}spb${ONAME} ]; then
		echo "photo2map" $f
		./photo2map.py -i $f -o ${OUT}spb${ONAME} -lat 59.9401 -lon 30.3715 -z 15 -w 2000 -j 4
	fi

	if [ ! -f ${OUT}msk${ONAME} ]; then
		echo "photo2map" $f
		./photo2map.py -i $f -o ${OUT}msk${ONAME} -lat 55.7447 -lon 37.6726 -z 10 -w 2000 -j 4
	fi
done


LAY="-layers merge -fill white -pointsize 80 -undercolor #0005 -gravity South -annotate +0+5 "

indexes=( spb msk )
for i in "${indexes[@]}"
do
	for f in ${OUT}${i}*.png
	do
		if [ ! -f ${OUT_MAP}`basename $f` ]; then
			echo "Adding map" $f
			convert -background transparent $f kartograph-test/${i}.svg ${LAY} `basename $f` ${OUT_MAP}`basename $f`
		fi
	done
done

convert $COL_COR $GIF_PARAM ${OUT}*.png ${OUT}animated.gif
convert $COL_COR $GIF_PARAM ${OUT_MAP}*.png ${OUT_MAP}animated.gif

echo "Done"
