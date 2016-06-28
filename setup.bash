BASEDIR=$(dirname "$0")
export PYTHONPATH=$BASEDIR:$BASEDIR/examples:$PYTHONPATH
export PATH=$BASEDIR/examples/scripts:$PATH

function _complete_rocktask {
    local arg opts
    COMPREPLY=()
    arg="${COMP_WORDS[COMP_CWORD]}"

    if [[ $COMP_CWORD == 1 ]]; then
        opts="list info start stop cleanup configure"
        COMPREPLY=($(compgen -W "$opts" -- ${arg}))
    elif [[ $COMP_CWORD == 2 ]]; then
        case ${COMP_WORDS[1]} in
            # complete on task name
            info|start|stop|cleanup|configure)
                opts=`rocktask list 2> /dev/null`
                COMPREPLY=($(compgen -W "$opts" -- ${arg}))                
                ;;
        esac
    fi
}

complete -F "_complete_rocktask" "rocktask"
