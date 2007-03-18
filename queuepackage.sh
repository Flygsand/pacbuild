#!/bin/sh
myver="0.4"

if [ ! -f $HOME/.queuepackage.conf ]; then
echo "Creating bare config in ~/.queuepackage.conf"
cat > $HOME/.queuepackage.conf << EOF
# This is the default config file for queuepackage (the pacbuild command line uploading tool)
# Change these values to be unique to you.  It will make things easier in the long run.

username=""
password=""

url="http://localhost:8888"

defaultpriority=1

defaultconfig=""

defaultarch=""
EOF

fi

source $HOME/.queuepackage.conf

USERNAME="$username"
PASSWORD="$password"
URL="$url"
CONFIG="$defaultconfig"
PRIORITY="$defaultpriority"
ARCH="$defaultarch"

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

usage() {
	echo "queuepackage version $myver"
	echo
	echo "Usage: $0 [options]"
	echo
	echo "Options:"
	echo "  -u <username>    Use this username when connecting to apple daemon"
	echo "  -p <password>    Use this password when connecting to apple daemon"
	echo "  -l <url>         Use this url when to connect to apple daemon"
	echo "  -c <config name> Use this config to build the package"
	echo "  -r <priority>    Set the build priority"
	echo "  -a <arch>        Build the package on this architecture"
	echo
	echo "A config file exists in ~/.queuepackage.conf to store defaults for all of these options"
	exit 1
}

while getopts "u:p:l:c:r:a:" opt; do
	case $opt in
		u) USERNAME="$OPTARG" ;;
		p) PASSWORD="$OPTARG" ;;
		l) URL="$OPTARG" ;;
		c) CONFIG="$OPTARG" ;;
		r) PRIORITY="$OPTARG" ;;
		a) ARCH="$OPTARG" ;;
		?) usage; exit 1 ;;
	esac
done

if [ "$USERNAME" = "" -o "$PASSWORD" = "" -o "$URL" = "" -o "$CONFIG" = "" -o "$PRIORITY" = "" -o "$ARCH" = "" ]; then
	usage
	exit 1
fi

if [ ! -f PKGBUILD ]; then
	echo "Please execute $0 in the package's directory"
	echo "Missing PKGBUILD"
	exit 1
fi

source PKGBUILD

files="PKGBUILD"

for i in *; do
	if [ "$i" != "CVS" -a "$i" != "PKGBUILD" ]; then
		in_source $i
		if [ $? -eq 0 ]; then
			files="$files $i"
		fi
	fi
done

tar czf $pkgname-$pkgver-$pkgrel.src.tar.gz $files
uploadPkgbuild.py "$URL" "$USERNAME" "$PASSWORD" "$ARCH" "$PRIORITY" "$CONFIG" $pkgname $pkgver $pkgrel $pkgname-$pkgver-$pkgrel.src.tar.gz
rm $pkgname-$pkgver-$pkgrel.src.tar.gz
