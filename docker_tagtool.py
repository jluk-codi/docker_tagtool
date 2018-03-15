from __future__ import print_function
import requests
import docker


def get_container_list(registry):
    catalog_req = requests.get('http://' + registry + '/v2/_catalog')
    catalog = catalog_req.json()
    return catalog["repositories"]

def get_tag_list(registry, container):
    catalog_req = requests.get('http://' + registry + '/v2/' + container + '/tags/list')
    catalog = catalog_req.json()
    return catalog["tags"]

def main():
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

if __name__ == "__main__":
    main()
