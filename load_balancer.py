from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, request, Response
from subprocess import Popen, PIPE
from io import BytesIO
from consistent_hash import ConsistantHash
from utils import (
    errHostnameListInconsistent,
    errInvalidRequest,
    get_container_rm_command,
    get_container_run_command,
    get_random_name,
    get_random_number,
    get_server_health,
    get_unhealty_servers,
    validateRequest,
)

import signal
import asyncio
import logging as log
import random
import base64
import matplotlib.pyplot as plt
import requests
import io


NETWORK_NAME = "load_balancer_network"

app = Flask(__name__)
consistant_hash = ConsistantHash()
servers = {'Server-1', 'Server-2', 'Server-3', 'Server-4'}
request_counts = {server: 0 for server in servers}

def check_servers():
    global servers

    log.debug("Checking server health...")
    unhealthy_servers = asyncio.run(get_unhealty_servers(servers))
    print("Unhealthy servers: ", unhealthy_servers, flush=True)
    for server in unhealthy_servers:
        print(f"Removing {server}", flush=True)
        command = get_container_rm_command(server, NETWORK_NAME)
        res = Popen(command, stdout=PIPE, stderr=PIPE)
        if res.returncode is not None:
            log.error(f"Error in adding {server}")
        else:
            log.info(f"Added {server}")
            servers.remove(server)
            request_counts.pop(server, None)

sched = BackgroundScheduler(daemon=True)
sched.add_job(check_servers, 'interval', seconds=30)
sched.start()

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return jsonify({}), 200

@app.route('/rep', methods=['GET'])
def rep():
    global servers

    healthy_servers = asyncio.run(get_server_health(servers))
    output = {
        'message': {
            'N': len(healthy_servers),
            'replicas': healthy_servers
        },
        'status': 'successful'
    }
    return jsonify(output), 200

@app.route('/add', methods=['POST'])
def add():
    global servers, request_counts

    n, hostnames, err = validateRequest(request)
    if err is errInvalidRequest:
        return jsonify({
            'message': '<Error> Request payload in invalid format',
            'status': 'failure'
        }), 400
    if err is errHostnameListInconsistent:
        return jsonify({
            'message': '<Error> Length of hostname list is more than newly added instances',
            'status': 'failure'
        }), 400

    random_servers = 0
    for hostname in hostnames:
        if hostname in servers:
            log.info(f"Server {hostname} already exists")
            random_servers += 1
            continue

        command = get_container_run_command(hostname, NETWORK_NAME)
        res = Popen(command, stdout=PIPE, stderr=PIPE)
        if res.returncode is not None:
            log.error(f"Error in adding {hostname}")
        else:
            servers.add(hostname)
            request_counts[hostname] = 0
            consistant_hash.add_server_to_hash(hostname)
            log.info(f"Added {hostname}")

    random_servers += n - len(hostnames)
    random_servers_up = 0
    while random_servers_up < random_servers:
        server_name = get_random_name(7)
        command = get_container_run_command(server_name)
        res = Popen(command, stdout=PIPE, stderr=PIPE)
        if res.returncode is not None:
            log.error(f"Error in adding server with random name {server_name}")
        else:
            servers.add(server_name)
            request_counts[server_name] = 0
            consistant_hash.add_server_to_hash(server_name)
            log.info(f"Added {server_name}")
        
    output = {
        'message': {
            'N': len(servers),
            'replicas': list(servers)
        },
        'status': 'successful'
    }
    return jsonify(output), 200

@app.route('/rm', methods=['POST'])
def rm():
    global servers, request_counts
    
    n, hostnames, err = validateRequest(request)
    if err is errInvalidRequest:
        return jsonify({
            'message': '<Error> Request payload in invalid format',
            'status': 'failure'
        }), 400
    if err is errHostnameListInconsistent:
        return jsonify({
            'message': '<Error> Length of hostname list is more than removable instances',
            'status': 'failure'
        }), 400
    
    random_servers = 0
    for hostname in hostnames:
        if hostname not in servers:
            log.info(f"Server {hostname} does not exist")
            random_servers += 1
            continue

        command = get_container_rm_command(hostname)
        res = Popen(command, stdout=PIPE, stderr=PIPE)
        if res.returncode is not None:
            log.error(f"Error in removing {hostname}")
        else:
            log.info(f"Removed {hostname}")
            consistant_hash.remove_server_from_hash(hostname, request_counts)
            servers.remove(hostname)
            request_counts.pop(hostname, None)

    random_servers += n - len(hostnames)
    random_servers_up = 0
    while random_servers_up < random_servers:
        server_name = random.choice(servers)
        command = get_container_rm_command(server_name)
        res = Popen(command, stdout=PIPE, stderr=PIPE)
        if res.returncode is not None:
            log.error(f"Error in removing random server with name {server_name}")
        else:
            log.info(f"Removed {server_name}")
            consistant_hash.remove_server_from_hash(server_name)
            servers.remove(server_name)
            request_counts.pop(server_name, None)

    output = {
        'message': {
            'N': len(servers),
            'replicas': list(servers)
        },
        'status': 'successful'
    }
    return jsonify(output), 200

@app.route('/checkpoint', methods=['GET'])
def checkpoint():
    global servers, request_counts
    output = {
        'servers': list(servers),
        'requests': request_counts
    }
    return jsonify(output), 200

@app.route('/home', methods=['GET'])
def home():
    global servers, request_counts

    server_name = consistant_hash.get_server_from_request(get_random_number(6))
    request_counts[server_name] += 1
    return jsonify({"message": f"Hello from {server_name}"}), 200


@app.route('/graph', methods=['GET'])
def generate_graph():
    global servers, request_counts
    
    # Create lists for servers and request counts
    server_names = list(servers)
    counts = [request_counts[server] for server in server_names]
    
    # Create a bar plot
    plt.bar(server_names, counts)
    plt.xlabel('Server Name')
    plt.ylabel('Requests Per Server')
    plt.title('Distribution of Requests Among Servers Using Updated Algorithm')
    
    # Save the plot to a byte buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Return the plot as a response
    return Response(buffer.getvalue(), mimetype='image/png')



if __name__ == '__main__':
    consistant_hash.build(servers)
    app.run(debug=True, host='0.0.0.0', port='5000')
