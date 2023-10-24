import os, requests


def token(request):
    if not "Authorization" in request.headers:
        return None, ("Missing credentials", 401)

    user_token = request.headers["Authorization"]

    if not user_token:
        return None, ("Missing credentials", 401)

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate", auth=user_token
    )

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
