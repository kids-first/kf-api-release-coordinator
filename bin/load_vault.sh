#!/bin/ash
if [[ -n $VAULT_ADDR ]] && [[ -n $VAULT_ROLE ]]; then
    echo "Found vault details in environment. Will try to load secrets"
    vault login -method=aws role=$VAULT_ROLE 2>&1 | grep authent

    # Build db connection string
    if [[ -n $PG_HOST ]] && [[ -n $PG_NAME ]] && [[ -n $PG_SECRET ]]; then
        echo "Load postgres connection from vault"
        secrets=$(vault read -format=json ${PG_SECRET} | jq -c '.')
        user=$(echo ${secrets} | jq -r '.data.user')
        pass=$(echo ${secrets} | jq -r '.data.password')

        export PG_USER=$user
        export PG_PASS=$pass
    fi

    # Get redis password
    if [[ -n $REDIS_SECRET ]] ; then
        echo "Load redis secret from vault"
        pw=$(vault read -format=json ${REDIS_SECRET} | jq -c '.password')

        export REDIS_PASS=$pw
    fi

    # Get ego secret
    if [[ -n $EGO_SECRET ]] ; then
        echo "Load ego secret from vault"
        client=$(vault read -format=json ${EGO_SECRET} | jq -c '.data.client_id')
        secret=$(vault read -format=json ${EGO_SECRET} | jq -c '.password.client_secret')

        export EGO_CLIENT_ID=$client
        export EGO_SECRET=$secret
    fi
fi
