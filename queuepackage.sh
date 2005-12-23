#!/bin/sh

in_source() {
	for j in ${source[@]}; do
		if [ "$j" == "$1" ]; then
			return 0
		fi
	done
	if [ "$1" == "$install" ]; then
		return 0
	fi

	return 1
}

source PKGBUILD

files="PKGBUILD"

for i in *; do
	if [ "$i" != "CVS" -a "$i" != "PKGBUILD" ]; then
		in_source $i
		if [ $? -eq 0 ]; then
			echo "adding $i"
			files="$files $i"
		fi
	fi
done

tar czf $pkgname-$pkgver-$pkgrel.src.tar.gz $files
uploadPkgbuild.py $1 $2 $3 $4 $pkgname $pkgver $pkgrel $pkgname-$pkgver-$pkgrel.src.tar.gz
