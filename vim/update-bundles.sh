#!/bin/sh
export n=1

echo "Bundle Updater v$VERSION"

for dir in ./*/ ; do 
    echo " ($n) Updating bundle $dir"
    cd $dir ;

    printf "\t>>> Running 'git fetch' in $PWD\n"
    git fetch &&\
    printf "\t>>> Fetch successful\n"
    cd ..;
    n=$((n+1))
done
