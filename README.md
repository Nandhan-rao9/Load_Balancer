# Load-Balancer - Distributed-Systems
### This repository contains the implementation of a load balancer using Docker, aimed at efficiently distributing requests among several servers. The load balancer routes requests from multiple clients asynchronously to ensure nearly even distribution of the load across the server replicas.

## Task Description
### TASK ONE: SERVER
* **Endpoint (/home, method=GET)**: This endpoint returns a string with a unique identifier to distinguish among the replicated server containers. For instance, if a client requests this endpoint and the load balancer schedules the request to Server: 3, then an example return string would be Hello from Server:
Hint: Server ID can be set as an env variable while running a container instance from the docker image of the server
   - Command: ```curl -X GET -H "Content-type: application/json" http://localhost:5000/home```
   - Response: ```{"message": "Hello from server_1"}}```
     
* **Endpoint (/heartbeat, method=GET)**: This endpoint sends heartbeat responses upon request. The load balancer further
uses the heartbeat endpoint to identify failures in the set of containers maintained by it. Therefore, you could send an empty
response with a valid response code.
  - Command: ```curl -X GET -H "Content-type: application/json" http://localhost:5000/heartbeat```
  - Response: ```{}```

### TASK TWO: CONSISTENT HASHING
 * In this task, you need to implement a consistent hash map using an array, linked list, or any other data structure. This map data
structure details are given in Appendix A. Use the following parameters and hash functions for your implementation.
    - Number of Server Containers managed by the load balancer (N) = 3
    - Total number of slots in the consistent hash map (#slots) = 512
    - Number of virtual servers for each server container (K) = log (512) = 9 2
    - Hash function for request mapping H(i) = i + 2i + 17 2 2
    - Hash function for virtual server mapping Φ(i, j) = i + j + 2j + 25

* **Consistant Hashing Algorithm Implementation**
    - Implementation Details:
      - Uses array-based data structure
      - Number of Server Containers (N): 3
      - Total number of slots in the consistent hash map (#slots): 512
      - Number of virtual servers for each server container (K): log(512) = 9
    - Hash functions used:
      - Hash function for request mapping H(i): H(i) = i + 2i + 17
      - Hash function for virtual server mapping Φ(i, j): Φ(i, j) = i + j + 2j + 25

### TASK THREE: LOAD BALANCER
* **Endpoint (/add, method=POST)**: This endpoint adds new server instances in the load balancer to scale up with increasing client numbers in the system. The endpoint expects a JSON payload that mentions the number of newinstances and their preferred hostnames (same as the container name in docker) in a list. An example request and response is below.
  - Command: ``` curl -X POST -H "Content-Type: application/json" --data-binary "{\"n\": 4, \"hostnames\": [\"server11\", \"server12\", \"server13\", \"new_servers4\"]}" http://localhost:5000/add ```
  - Response: ```{"message": {"N": 5,"replicas": ["server12","new_servers4","server_1","server11","server13"]},
  "status": "successful"}```
  * Perform simple sanity checks on the request payload and ensure that hostnames mentioned in the Payload are less than or equal to newly added instances. Note that the hostnames are preferably set. One can never set the hostnames. In that case, the hostnames (container names) are set randomly. However, sending a hostname list with greater length than newly added instances will result in an error.
    - Command: ```curl -X POST -H "Content-Type: application/json" --data-binary "{\"n\": 2, \"hostnames\": [\"server11\", \"server12\", \"server13\", \"new_servers4\"]}" http://localhost:5000/add```
    - Response: ```{"message": "<Error> Length of hostname list is more than newly added instances","status": "failure"}```

* **Endpoint (/rep, method=GET)**: This endpoint only returns the status of the replicas managed by the load balancer. The response contains the number of replicas and their hostname in the docker internal network:n1 as mentioned in Fig. 1. An example response is shown below.
  - Command: ``` curl -X GET -H "Content-type: application/json" http://localhost:5000/rep ```
  - Response: ```{"message": {"N": 0,"replicas": []},"status": "successful"}```


