"""
List unhealthy services in your ECS clusters

The script will list the clusters and fetch details about services that are
running in it.
Then it determines if the service is healthy or not:
* the service status must be ACTIVE
* the service must have a non-empty events list
* the service desiredCount equals its runningCount
* the last event message of the service ends with 'has reached a steady state.'

Usage:

    # List unhealthy services in all ECS clusters
    $ ecs_monitor.py

    # List unhealthy services in ECS clusters that contains 'dev' in their name
    $ ecs_monitor.py --filter dev
"""

from __future__ import print_function
from argparse import ArgumentParser

import boto3

ECS_CLIENT = boto3.client('ecs')
AWS_PAGE_SIZE = 10


class Colors:
    RESET = '\033[0;0m'
    OK = '\033[0;32m'
    WARN = '\033[0;33m'
    ERROR = '\033[1;31m'


class EcsService(object):
    """
    Utility class that represents an ECS Service.
    """
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def active(self):
        """
        Check that `service` is active in ECS.
        """
        return self.status.upper() == 'ACTIVE'

    def is_up(self):
        """
        Check that `service` in ECS is running and stable.

        The `service` is stable when the last event message ends with 'has reached a
        steady state.' and its runningCount equals its desiredCount.
        """
        return (
            self.desiredCount == self.runningCount and
            self.events and
            self.events[0]['message'].endswith('has reached a steady state.')
        )

    def is_down(self):
        """
        Check that `service` in ECS is down or unstable.
        """
        return not self.is_up()

    def status_to_text(self):
        status_line = '{begin}{text}{end}'
        if self.is_up():
            status = status_line.format(begin=Colors.OK, text='[OK]', end=Colors.RESET)
        else:
            status = status_line.format(begin=Colors.ERROR, text='[KO]', end=Colors.RESET)
        if self.is_up() and self.runningCount == 0:
            status = status_line.format(begin=Colors.WARN, text='[WARN]', end=Colors.RESET)
        return status

    def details(self):
        return '{status:20s} {service:50s} desired {desired} / running {running}'.format(
            status=self.status_to_text(), service=self.serviceName,
            desired=self.desiredCount, running=self.runningCount)


def chunk(iterable, size=AWS_PAGE_SIZE):
    """
    Split an `iterable` into chunks of `size` items

    :param iterable: the iterable that is split
    :param size: the maximum number of items in each chunk
    """
    return (iterable[pos:pos + size] for pos in xrange(0, len(iterable), size))


def __paginate_call(client, method, output_key, params=None):
    """
    Paginate a Boto3 API call on a given method to return a flat list.
    """
    def is_response_success(response):
        return response['ResponseMetadata']['HTTPStatusCode'] == 200

    params = dict() if params is None else params
    params['PaginationConfig'] = dict(PageSize=AWS_PAGE_SIZE)

    paginator = client.get_paginator(method)
    responses = list(paginator.paginate(**params))

    if not all([is_response_success(r) for r in responses]):
        raise Exception('Error during execution of method {method}'.format(method=method))

    responses = [r[output_key] for r in responses]
    return reduce(lambda x, y: x + y, responses)


def list_clusters(_filter=None):
    """
    Return available clusters in the AWS account.

    :param _filter: filters on any part of the name of the cluster
    """
    ecs_clusters = __paginate_call(ECS_CLIENT, 'list_clusters', 'clusterArns')
    if _filter:
        ecs_clusters = [cluster for cluster in ecs_clusters if _filter in cluster]
    return sorted(ecs_clusters)


def services_in_cluster(cluster):
    """
    Return running services in the ECS cluster named `cluster`.

    :param cluster: the cluster name or the cluster ARN
    """
    params = {'cluster': cluster}
    deployed_services = __paginate_call(ECS_CLIENT, 'list_services', 'serviceArns', params)
    return [
        EcsService(**service)
        for services in chunk(deployed_services)
        for service in ECS_CLIENT.describe_services(cluster=cluster, services=services)['services']
    ]


def parse_args():
    """
    Parse command line arguments.
    """
    parser = ArgumentParser(description='List unhealthy services in your ECS clusters.')
    parser.add_argument('-f', '--filter', required=False)
    return parser.parse_args()


def main():
    """
    Main function.
    """
    args = parse_args()
    clusters = list_clusters(args.filter)

    for cluster in clusters:
        deployed_services = services_in_cluster(cluster)
        services = [
            s for s in sorted(deployed_services, key=lambda s: s.serviceName)
            if s.active()
        ]

        cluster_name = cluster.split('/')[-1].upper()
        print('---- {cluster} : {size} services'.format(
            cluster=cluster_name, size=len(deployed_services)))

        for service in services:
            print(service.details())

        print('')


if __name__ == '__main__':
    main()
