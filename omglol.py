from thttp import request


def update_now_page(username, content, api_key):
    response = request(
        f"https://api.omg.lol/address/{username}/now",
        method="POST",
        json={"content": content},
        headers={"Authorization": f"Bearer {api_key}"},
    )
    print(response.json)


def get_now_page(username):
    response = request(f"https://api.omg.lol/address/{username}/now")
    return response.json["response"]["now"]
