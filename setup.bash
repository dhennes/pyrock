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
            info|start|stop|cleanup|configure)
                if [[ ${arg} =~ \-\-.* ]]; then
                    opts="--help"
                else
                    # complete on task name
                    opts=`rocktask list 2> /dev/null`
                fi
                COMPREPLY=($(compgen -W "$opts" -- ${arg}))
                ;;
            list)
                if [[ ${arg} =~ \-\-.* ]]; then
                    opts="--state --help"
                fi
                COMPREPLY=($(compgen -W "$opts" -- ${arg}))
                ;;
        esac
    fi
}

complete -F "_complete_rocktask" "rocktask"
