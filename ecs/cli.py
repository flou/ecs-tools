#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Command line tool to interact with AWS ECS.
"""

import click
from . import ecs


@click.command('scale-service')
@click.option('--cluster', help='Name of the ECS cluster', required=True)
@click.option('--service', help='Name of the service', required=True)
@click.argument('count', type=click.IntRange(0, None))
def scale_service(cluster, service, count):
    """
    Scale the service to a specific desiredCount.
    """
    ecs.update_service(cluster, service, count)


@click.command()
@click.option('cluster_filter', '--filter', '-f', help='Filter by the name of the ECS cluster')
def monitor(cluster_filter):
    """
    List unhealthy services in your ECS clusters.
    """
    clusters = ecs.list_clusters(cluster_filter)

    for cluster in clusters:
        deployed_services = ecs.services_in_cluster(cluster)
        services = [
            s for s in sorted(deployed_services, key=lambda s: s.service_name)
            if s.active()
        ]

        cluster_name = cluster.split('/')[-1].upper()
        click.echo('---- {cluster} : {size} services'.format(
            cluster=cluster_name, size=len(deployed_services)))

        for service in services:
            click.echo(service.details())

        click.echo('')




@click.group()
def main():
    pass

main.add_command(scale_service)
main.add_command(monitor)

if __name__ == '__main__':
    main()
