import socket
import ssl
import json

def make_request(host, port, request):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                ssock.sendall(request.encode())
                response = ssock.recv(4096)
                full_response = b""
                while response:
                    full_response += response
                    response = ssock.recv(4096)
                return full_response
    except socket.gaierror:
        return "Error: Не удается разрешить доменное имя."
    except socket.timeout:
        return "Error: Сервер слишком долго не отвечал."
    except Exception as exc:
        return f"Error: {exc}"


def vk_api_request(method, params, access_token):
    host = 'api.vk.com'
    port = 443
    url_path = f"/method/{method}?{params}&access_token={access_token}&v=5.131"
    request = f"GET {url_path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

    response = make_request(host, port, request)
    if response.startswith("Error:"):
        return response

    response_str = response.decode()
    headers, body = response_str.split("\r\n\r\n", 1)

    return json.loads(body)

def get_user_friends(user_id, access_token):
    method = "friends.get"
    params = f"user_id={user_id}&fields=nickname"
    response = vk_api_request(method, params, access_token)
    if isinstance(response, str) and response.startswith("Error:"):
        return response

    friends = response['response']['items']
    return [f"{friend['first_name']} {friend['last_name']}" for friend in friends]

def get_user_albums(user_id, access_token):
    method = "photos.getAlbums"
    params = f"owner_id={user_id}"
    response = vk_api_request(method, params, access_token)
    if isinstance(response, str) and response.startswith("Error:"):
        return response

    albums = response['response']['items']
    return [album['title'] for album in albums]

if __name__ == "__main__":
    access_token = "YOUR_ACCESS_TOKEN"
    user_id = "USER_ID"

    print("Собирание друзей...")
    friends = get_user_friends(user_id, access_token)
    if isinstance(friends, str) and friends.startswith("Error:"):
        print(friends)
    else:
        print("Список друзей:")
        for friend in friends:
            print(friend)

    print("\nВыборка альбомов...")
    albums = get_user_albums(user_id, access_token)
    if isinstance(albums, str) and albums.startswith("Error:"):
        print(albums)
    else:
        print("Список альбомов:")
        for album in albums:
            print(album)