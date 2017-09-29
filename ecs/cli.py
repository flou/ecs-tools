#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Command line tool to interact with AWS ECS.
"""

import click
from . import ecs, VERSION


@click.group()
@click.version_option(VERSION, '-v', '--version')
@click.help_option('-h', '--help')
def cli():
    pass


@cli.command()
@click.option('--cluster', help='Name of the ECS cluster', required=True)
@click.option('--service', help='Name of the service', required=True)
def image(cluster, service):
    """
    Return the image for a service.
    """
    click.echo(ecs.find_image(cluster, service))


@cli.command('scale-service')
@click.option('--cluster', help='Name of the ECS cluster', required=True)
@click.option('--service', help='Name of the service', required=True)
@click.argument('count', type=click.IntRange(0, None))
def scale_service(cluster, service, count):
    """
    Scale the service to a specific desiredCount.
    """
    ecs.update_service(cluster, service, count)


@cli.command()
@click.option('cluster_filter', '--filter', '-f', help='Filter by the name of the ECS cluster')
@click.option('threshold', '--threshold', '-t', help='Filter by the status of the service')
@click.option('long_output', '--long', '-l', is_flag=True, help='Enable detailed output of containers parameters')
@click.option('all_services', '--all', '-a', is_flag=True, help='Display status for all services in the cluster')
def monitor(cluster_filter, threshold, long_output=False, all_services=False):
    """
    List unhealthy services in your ECS clusters.
    """
    clusters = ecs.list_clusters(cluster_filter)

    for cluster in clusters:
        deployed_services = ecs.services_in_cluster(cluster)
        services = [
            s for s in sorted(deployed_services, key=lambda s: s.service_name)
            if s.active
        ]

        cluster_name = cluster.split('/')[-1].upper()
        click.echo('---- {cluster} : {size} services'.format(
            cluster=cluster_name, size=len(deployed_services)))

        for service in services:
            if service.status in ['WARN', 'KO'] or all_services:
                click.echo(service.details())
                if long_output:
                    click.echo(service.containers())

        click.echo('')


if __name__ == '__main__':
    cli()
