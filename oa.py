import os

from authlib.integrations.flask_client import OAuth

oauth = OAuth()


def github():
    oauth.register(
        name='github',
        client_id=os.getenv("GITHUB_CONSUMER_KEY"),
        client_secret=os.getenv("GITHUB_CONSUMER_SECRET"),
        api_base_url="https://api.github.com/",
        access_token_params=None,
        authorize_params=None,
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        client_kwargs={
            "scope": "user:email",
            "token_endpoint_auth_method": "client_secret_basic",
        },
    )

    return oauth.create_client('github')
