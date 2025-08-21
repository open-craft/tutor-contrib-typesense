#! /bin/sh

while true; do
    RESPONSE_CODE="$(curl --silent --show-error -o /dev/null -w '%{http_code}' -X GET -H 'X-TYPESENSE-API-KEY: {{ TYPESENSE_API_KEY }}' 'http://typesense:8108/debug' || true)"
    case "$RESPONSE_CODE" in
        401)
            if curl -X POST 'http://typesense:8108/keys' \
                --silent --show-error -o /dev/null --fail -w '\n' \
                -H 'Content-Type: application/json' \
                -H 'X-TYPESENSE-API-KEY: {{ TYPESENSE_BOOTSTRAP_API_KEY }}' \
                --data-binary '{
                    "value": "{{ TYPESENSE_API_KEY }}",
                    "description": "Open edX key for {{ LMS_HOST }}",
                    "actions": ["*"],
                    "collections": ["^{{ TYPESENSE_COLLECTION_PREFIX }}.*"]
                }'; then
                echo 'Typesense API key created.'
                exit
            else
                echo 'Failed to create Typesense API key.'
                exit 1
            fi
            ;;
        200)
            echo 'Typesense API key already exists.'
            exit
            ;;
        *)
            echo "Received unexpected HTTP response ($RESPONSE_CODE) from Typesense; retrying in 5 seconds."
            sleep 5
    esac
done
