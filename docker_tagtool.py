from __future__ import print_function
import requests
import docker
import sys


def get_container_list(registry):
    catalog_req = requests.get('http://' + registry + '/v2/_catalog')
    catalog = catalog_req.json()
    return catalog["repositories"]

def get_tag_list(registry, container):
    catalog_req = requests.get('http://' + registry + '/v2/' + container + '/tags/list')
    catalog = catalog_req.json()
    return catalog["tags"]

def tag():
    client = docker.from_env()
    registry = "localhost:5000"
    tag = 'ocata-master-29'
    tag_short = 'master-29'
    registry_containers = get_container_list(registry)
    print(registry_containers)
    contrail_containers = [ x for x in registry_containers if x.startswith('contrail-')]
    print(contrail_containers)
    current_containers = []
    for container in contrail_containers:
        tags = get_tag_list(registry, container)
        print(tags)
        if tag in tags:
            current_containers.append(container)
    print(current_containers)
    for cont in current_containers:
        print('Processing', cont)
        pulled = client.images.pull(registry + '/' + cont, tag=tag)
        for t in [tag, tag_short]:
            print('Tagging', cont, t)
            pulled.tag('opencontrailnightly/' + cont, tag=t)
            print('Pushing', cont, t)
            ret = client.images.push('opencontrailnightly/' + cont, tag=t)
    # push latest tags as the last step to minimize time of inconsistent tagging
    for cont in current_containers:
        print('Processing', cont)
        t = 'latest'
        print('Tagging', cont, t)
        pulled.tag('opencontrailnightly/' + cont, tag=t)
        print('Pushing', cont, t)
        ret = client.images.push('opencontrailnightly/' + cont, tag=t)
    conts = client.containers.list()
    #print(conts)

def clearcontainers():
    client = docker.from_env()
    containers = client.containers.list()
    print("Will delete containers:")
    [print(c.name, c.image) for c in containers]
    print("Ok?")
    sys.stdin.readline()
    retries = 3
    for container in containers:
        for i in range(retries):
            try:
                print("Stopping", container.name, i, '...')
                container.stop()
                print("Removing", container.name, i, '...')
                container.remove()
                break
            except Exception as e:
                pass

def clearimages():
    images = client.images.list()
    print("Will delete images:")
    [print(c.name) for c in images]
    print("Ok?")
    sys.stdin.readline()

def clearall():
    clearcontainers()
    clearimages()


def main(cmd):
    if cmd == "tag":
        tag()
    elif cmd == "clearall":
        clearall() 
    elif cmd == "clearcontainers":
        clearcontainers() 
    elif cmd == "clearimages":
        clearimages() 

if __name__ == "__main__":
    cmd = sys.argv[1]
    main(cmd)
