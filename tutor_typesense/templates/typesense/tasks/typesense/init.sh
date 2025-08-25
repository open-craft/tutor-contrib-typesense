#! /bin/sh

if curl -s -o /dev/null -w '%{http_code}' -X GET -H 'X-TYPESENSE-API-KEY: {{ TYPESENSE_API_KEY }}' 'http://typesense:8108/debug' | grep '401'; then
    curl -X POST 'http://typesense:8108/keys' \
        --fail-with-body -w '\n' \
        -H 'Content-Type: application/json' \
        -H 'X-TYPESENSE-API-KEY: {{ TYPESENSE_BOOTSTRAP_API_KEY }}' \
        --data-binary '{
            "value": "{{ TYPESENSE_API_KEY }}",
            "description": "Open edX key for {{ LMS_HOST }}",
            "actions": ["*"],
            "collections": ["^{{ TYPESENSE_COLLECTION_PREFIX }}.*"]
        }' && echo 'Typesense API key created.' || (echo 'Failed to create Typesense API key.'; exit 1)
else
    echo 'Typesense API key already exists.'
fi
