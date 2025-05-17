main
from flask import Request
import asyncio
import httpx
import random
import string

errInvalidRequest = "Invalid request"
errHostnameListInconsistent = "Hostname List Inconsistent"

def validateRequest(request: Request):
    req = request.get_json()

    if req['n'] is None or req['n'] <= 0:
        return None, None, errInvalidRequest
    if req['n'] > 0 and len(req['hostnames']) > req['n']:
        return None, None, errHostnameListInconsistent
    
    if req['hostnames'] is None:
        return req['n'], [], None
    
    return req['n'], req['hostnames'], None

async def fetch_url(url) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5)
            response.raise_for_status()
            return True
        except:
            return False

async def fetch_all_urls(urls) -> list[bool]:
    tasks = [asyncio.create_task(fetch_url(url)) for url in urls]
    responses = await asyncio.gather(*tasks)
    return responses

async def get_server_health(servers: list[str]) -> list[str]:
    urls = [f"http://{server}:5000/heartbeat" for server in servers]
    responses = await fetch_all_urls(urls)
    
    output: list[str] = []

    for server, result in zip(servers, responses):
        if result == True:
            output.append(server)

    return output

async def get_unhealty_servers(servers: list[str]) -> set[str]:
    urls = [f"http://{server}:5000/heartbeat" for server in servers]
    responses = await fetch_all_urls(urls)
    
    output: set[str] = set()

    for server, result in zip(servers, responses):
        if result == False:
            output.add(server)

    return output

def get_container_run_command(hostname: str, network_name: str) -> list[str]:
    output = ["sudo", "docker", "run",
              "--name", hostname,
              "--network", network_name,
              "--network-alias", hostname,
              "-e", f"SERVER_ID={hostname}",
              "-d", "server"
              ]
    return output

def get_container_rm_command(hostname: str) -> list[str]:
    output = ["sudo", "docker", "rm", "-f", hostname]
    return output

def get_random_name(length: int) -> str:
    output = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    return output

def get_random_number(length: int) -> int:
    output = ''.join(random.choices(string.digits, k=length))
    
=======
from flask import Request
import asyncio
import httpx
import random
import string

errInvalidRequest = "Invalid request"
errHostnameListInconsistent = "Hostname List Inconsistent"

def validateRequest(request: Request):
    req = request.get_json()

    if req['n'] is None or req['n'] <= 0:
        return None, None, errInvalidRequest
    if req['n'] > 0 and len(req['hostnames']) > req['n']:
        return None, None, errHostnameListInconsistent
    
    if req['hostnames'] is None:
        return req['n'], [], None
    
    return req['n'], req['hostnames'], None

async def fetch_url(url) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5)
            response.raise_for_status()
            return True
        except:
            return False

async def fetch_all_urls(urls) -> list[bool]:
    tasks = [asyncio.create_task(fetch_url(url)) for url in urls]
    responses = await asyncio.gather(*tasks)
    return responses

async def get_server_health(servers: list[str]) -> list[str]:
    urls = [f"http://{server}:5000/heartbeat" for server in servers]
    responses = await fetch_all_urls(urls)
    
    output: list[str] = []

    for server, result in zip(servers, responses):
        if result == True:
            output.append(server)

    return output

async def get_unhealty_servers(servers: list[str]) -> set[str]:
    urls = [f"http://{server}:5000/heartbeat" for server in servers]
    responses = await fetch_all_urls(urls)
    
    output: set[str] = set()

    for server, result in zip(servers, responses):
        if result == False:
            output.add(server)

    return output

def get_container_run_command(hostname: str, network_name: str) -> list[str]:
    output = ["sudo", "docker", "run",
              "--name", hostname,
              "--network", network_name,
              "--network-alias", hostname,
              "-e", f"SERVER_ID={hostname}",
              "-d", "server"
              ]
    return output

def get_container_rm_command(hostname: str) -> list[str]:
    output = ["sudo", "docker", "rm", "-f", hostname]
    return output

def get_random_name(length: int) -> str:
    output = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    return output

def get_random_number(length: int) -> int:
    output = ''.join(random.choices(string.digits, k=length))
    
main
    return int(output)