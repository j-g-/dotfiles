#!/bin/sh
BLIST="${PWD}/bundle-list.txt"

# Checking for list of bundles url to exist
[ -e $BLIST ] || touch $BLIST


# This functions adds the url of the origin of a bundle git repository
add_tolist(){ 
    #$1: repo_url $2: repo_dir
    repo_url= $1 
    repo_dir= $2 
    echo ${repo_url }>> $BLIST && echo "Bundle ${repo_dir} wasn't in list" &&\
        echo "  URL: ${repo_url} added!"
}



export n=1
for dir in ./*/ ; do 
    echo " ($n) Updating bundle $dir"
    cd $dir ;

    printf "\t>>> Running 'git fetch' in $PWD\n"
    ORIGIN_URL=$(git remote show origin | grep Fetch | cut -c 14-) 
    echo "descargando desde $ORIGIN_URL"
    git fetch &&  printf "\t>>> Fetch successful\n"
    cd .. ;
    n=$((n+1))

    # Add to $BLIST if it's not there
    grep -q $ORIGIN_URL $BLIST ||  add_tolist $ORIGIN_URL $dir
done


