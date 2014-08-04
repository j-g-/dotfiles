#!/bin/sh
BLIST="$PWD/bundle-list.txt"

# Checking for list of bundles url to exist
[ -e $BLIST ] || touch $BLIST

echo "Bundle Updater v$VERSION"

# This functions adds the url of the origin of a bundle git repository
add_tolist(){ 
    #$1: repo_url $2: repo_dir
    echo $1 >> $BLIST && echo "Bundle $2 wasn't in list" &&\
        echo "  URL: $1 added!"
}



export n=1
for dir in ./*/ ; do 
    echo " ($n) Updating bundle $dir"
    cd $dir ;

    printf "\t>>> Running 'git fetch' in $PWD\n"
    ORIGIN_URL=$(git remote show origin | grep Fetch | cut -c 14-) 
    echo "descargando desde $ORIGIN_URL"
    git fetch &&\
    printf "\t>>> Fetch successful\n"
    cd ..;
    n=$((n+1))
    grep -q $ORIGIN_URL $BLIST ||  add_tolist $ORIGIN_URL $dir
    
done


