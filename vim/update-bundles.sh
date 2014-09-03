#!/bin/sh
source ~/.bash_colors
BLIST="${PWD}/bundle-list.txt"

# Checking for list of bundles url to exist
[ -e $BLIST ] || touch $BLIST


# This functions adds the url of the origin of a bundle git repository
add_tolist(){ 
    #$1: repo_url $2: repo_dir
    repo_url="${1}"
    repo_dir="${2}"
    echo -e "${CRed}>>>${CYellow} Bundle ${repo_dir} wasn't in list" 
    echo -e "  URL: ${CGreen} ${repo_url} ${CNone} adding!"
    echo "${repo_url}" >> $BLIST 
}



n=1
for dir in ./*/ ; do 
    echo -e "(${CGreen}${n}${CNone}) Updating bundle ${CAqua}$dir${CNone}"
    cd $dir ;

    ORIGIN_URL=$(git remote show origin | grep Fetch | cut -c 14-) 
    printf "${CRed}>>>${CNone} Running ${CGreen}'git fetch'${CNone} in $PWD\n"
    printf "${CRed}>>>${CNone} descargando desde ${CAqua} ${ORIGIN_URL}${CNone}\n"
    git fetch &&  printf "${CRed}>>> ${CGreen}Fetch successful${CNone}\n" &&\
        git pull 
    cd .. ;
    n=$((n+1))

    # Add to $BLIST if it's not there
    grep -q $ORIGIN_URL $BLIST ||  add_tolist $ORIGIN_URL $dir
done


