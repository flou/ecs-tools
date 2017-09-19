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
import os
import sys

import boto3
import click
import crayons
import yaml

ECS_CLIENT = boto3.client('ecs')
AWS_PAGE_SIZE = 10


class EcsService(object):
    """
    Utility class that represents an ECS Service.
    """

    def __init__(self, **kwargs):
        self.service_name = kwargs['serviceName']
        self.events = kwargs['events']
        self.active = kwargs['status'].upper() == 'ACTIVE'
        self.desired_count = kwargs['desiredCount']
        self.running_count = kwargs['runningCount']
        self.task_definition = kwargs['taskDefinition'].split('/')[-1]
        self.cluster = kwargs['cluster'].partition(':cluster/')[-1]
        self.status = 'KO'
        if self.is_up() and self.running_count == 0:
            self.status = 'WARN'
        if self.is_up() and self.running_count > 0:
            self.status = 'OK'
        self.taskdef = ECS_CLIENT.describe_task_definition(taskDefinition=self.task_definition)['taskDefinition']

    def containers(self):
        containers = self.taskdef['containerDefinitions']
        out = ''
        for cont in containers:
            out += 'Name:         {}\n'.format(crayons.yellow(cont['name']))
            out += 'Docker image: {}\n'.format(crayons.yellow(cont['image']))
            out += 'Memory:       {}\n'.format(crayons.yellow(cont['memory']))
            out += 'CPU:          {}\n'.format(crayons.yellow(cont['cpu']))
            out += yaml.safe_dump(
                {'Environment': self._service_environment(cont)},
                default_flow_style=False)
        return out

    def service_images(self):
        return '\n'.join(c['image'] for c in self.taskdef['containerDefinitions'])

    def _service_environment(self, container):
        result = {}
        for env in container['environment']:
            for k, val in env.items():
                if k == 'name':
                    key = val
                if k == 'value':
                    value = val
            result[key] = value
        return result

    def link_to_ecs_console(self):
        """
        Return a link to the service on the ECS console.
        """
        region = os.environ.get('AWS_DEFAULT_REGION', 'eu-west-1')
        url = 'https://{0}.console.aws.amazon.com/ecs/home?{0}#/clusters/{1}/services/{2}/events'
        return url.format(region, self.cluster, self.service_name)

    def is_up(self):
        """
        Check that `service` in ECS is running and stable.

        The `service` is stable when the last event message ends with 'has reached a
        steady state.' and its runningCount equals its desiredCount.
        """
        return (
            self.desired_count == self.running_count and
            self.events and
            self.events[0]['message'].endswith('has reached a steady state.')
        )

    def is_down(self):
        """
        Check that `service` in ECS is down or unstable.
        """
        return not self.is_up()

    def status_to_text(self):
        """
        Check that `service` in ECS is down or unstable.
        """
        status = ''
        if self.is_up():
            status = crayons.green('[OK]')
        else:
            status = crayons.red('[KO]')
        if self.is_up() and self.running_count == 0:
            status = crayons.yellow('[WARN]')
        return status

    def details(self):
        """
        Return the line detailing the status of the service.
        """
        status_line = '{status:27s} {service:70s} running {running}/{desired} ({taskdef})'
        return status_line.format(
            status=self.status_to_text(), service=crayons.yellow(self.service_name),
            desired=self.desired_count, running=self.running_count,
            taskdef=self.task_definition)


def chunk(iterable, size=AWS_PAGE_SIZE):
    """
    Split an `iterable` into chunks of `size` items

    :param iterable: the iterable that is split
    :param size: the maximum number of items in each chunk
    """
    return (iterable[pos:pos + size] for pos in xrange(0, len(iterable), size))


def _is_response_success(response):
    return response['ResponseMetadata']['HTTPStatusCode'] == 200


def _paginate_call(client, method, output_key, params=None):
    """
    Paginate a Boto3 API call on a given method to return a flat list.
    """
    params = dict() if params is None else params
    params['PaginationConfig'] = dict(PageSize=AWS_PAGE_SIZE)

    paginator = client.get_paginator(method)
    responses = list(paginator.paginate(**params))

    if not all([_is_response_success(r) for r in responses]):
        raise Exception('Error during execution of method {method}'.format(method=method))

    responses = [r[output_key] for r in responses]
    return reduce(lambda x, y: x + y, responses)


def list_clusters(_filter=None):
    """
    Return available clusters in the AWS account.

    :param _filter: filters on any part of the name of the cluster
    """
    ecs_clusters = _paginate_call(ECS_CLIENT, 'list_clusters', 'clusterArns')
    if _filter:
        ecs_clusters = [cluster
                        for cluster in ecs_clusters
                        if _filter.lower() in cluster.split('/')[-1].lower()]
    return sorted(ecs_clusters)


def services_in_cluster(cluster):
    """
    Return running services in the ECS cluster named `cluster`.

    :param cluster: the cluster name or the cluster ARN
    """
    params = {'cluster': cluster}
    deployed_services = _paginate_call(ECS_CLIENT, 'list_services', 'serviceArns', params)
    return [
        EcsService(cluster=cluster, **service)
        for services in chunk(deployed_services)
        for service in ECS_CLIENT.describe_services(cluster=cluster, services=services)['services']
    ]


def find_service(cluster, service_name):
    """
    :param cluster: the cluster name or the cluster ARN
    :param service_name: the name of the service in the ECS cluster

    returns the EcsService or None if the service does not exist / or the cluster does not exist
    """
    try:
        srv = ECS_CLIENT.describe_services(cluster=cluster, services=[service_name])['services'][0]
        return EcsService(cluster=cluster, **srv)
    except IndexError:
        click.echo(crayons.red('No service {0} is running on cluster {1}'.format(service_name, cluster)), err=True)
        sys.exit(1)
    except ECS_CLIENT.exceptions.ClusterNotFoundException:
        click.echo(crayons.red('Cluster {0} does not exist'.format(cluster)), err=True)
        sys.exit(1)


def update_service(cluster, service, desired_count):
    """
    Update the desiredCount property of the ECS service.
    """
    running_service = find_service(cluster, service)
    if desired_count == running_service.desired_count:
        click.echo('Service {0} already has a desiredCount of {1}'.format(crayons.yellow(service), desired_count))
        sys.exit(0)

    click.echo(crayons.yellow('Updating {0} / desiredCount[{1} -> {2}] running_count={3}'.format(service, desired_count, running_service.desired_count, running_service.running_count)))
    response = ECS_CLIENT.update_service(
        cluster=cluster,
        service=service,
        desiredCount=desired_count
    )
    click.echo()
    if _is_response_success(response):
        click.echo('Service {0} successfully updated with desired_count={1}'.format(service, desired_count))
    else:
        click.echo(crayons.red('Service {0} could not be updated. Please check the AWS console'.format(service)), err=True)
        sys.exit(1)


def find_image(cluster, service):
    """
    Return the images for the ECS service.
    """
    running_service = find_service(cluster, service)
    return running_service.service_images()
