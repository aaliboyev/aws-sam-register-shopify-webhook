import json
import shopify


def lambda_handler(event, context):

    data = json.loads(event['body']) if type(event['body']) is str else event['body']

    if not all (k in data for k in ['shopUrl', 'apiVersion', 'token']):
        return {
            "statusCode": 422,
            "body": json.dumps({
                "message": "shopUrl, apiVersion and token are required to be sent in request body",
            }),
        }

    try: 
        session = shopify.Session(data['shopUrl'], data['apiVersion'], data['token'])
        shopify.ShopifyResource.activate_session(session)
    
        # We don't need to check webhook existance in shopify because shopify does not duplicate webhooks
        # if same webhook data is passed, shopify does not change anything
        # Here we send default example data if nothing passed in request body
        body = {
            'topic': data['webhookTopic'] if 'webhookTopic' in data else "orders/create",
            'address': data['webhookAddress'] if 'webhookAddress' in data else 'https://random.com/',
            'format': data['webhookFormat'] if 'webhookFormat' in data else 'json'
        }
        webhook = shopify.Webhook.create(body)

        shopify.ShopifyResource.clear_session()
    except Exception as e:
        return {
            "statusCode": int(e.code),
            "body": json.dumps({
                "message": "Error occured while connecting to shopify api",
                **json.loads(e.response.body)
            }),
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"New webhook registered successfully with id={webhook.id}" if webhook.id 
            else f"New webhook was not created. This may happen when invalid webhookTopic, " \
            "webhookAddress or webhookFormat was passed or else webhook with this topic and address already exists.",
        }),
    }