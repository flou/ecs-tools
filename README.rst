ECS tools
=========

Usage
~~~~~

::

    Usage: ecs [OPTIONS] COMMAND [ARGS]...

    Options:
      -v, --version  Show the version and exit.
      -h, --help     Show this message and exit.

    Commands:
      image          Return the image for a service.
      monitor        List unhealthy services in your ECS clusters.
      scale-service  Scale the service to a specific desiredCount.


Image
-----

Returns the image(s) that are defined in the currently running TaskDefinition.

Usage
~~~~~

::

    Usage: ecs image [OPTIONS]

      Return the image for a service.

    Options:
      --cluster TEXT  Name of the ECS cluster  [required]
      --service TEXT  Name of the service  [required]
      --help          Show this message and exit.

::

    $ ecs image --cluster ecs-mycluster-dev --service tools-deployment-dev-1
    123456789012.dkr.ecr.us-east-1.amazonaws.com/acme/srv-tools-deployment:1.0.3

Monitor
----------

ECS monitor lists unhealthy services in your ECS clusters

The script will list the clusters and fetch details about services that are
running in it.

Then it determines if the service is healthy or not:

* ``[OK]`` means that its ``desiredCount`` equals its ``runningCount`` and it has
  reached a steady state
* ``[WARN]`` means that its ``desiredCount`` and its ``runningCount`` equal 0 but it
  still has reached a steady state
* ``[KO]`` means that its ``desiredCount`` does not equal its ``runningCount``, or
  that it has not reached a steady state


Usage
~~~~~

::

    Usage: ecs monitor [OPTIONS]

      List unhealthy services in your ECS clusters.

    Options:
      -f, --filter TEXT     Filter by the name of the ECS cluster
      -t, --threshold TEXT  Filter by the status of the service
      -l, --long            Enable detailed output of containers parameters
      -a, --all             Display status for all services in the cluster
      --help                Show this message and exit.


List unhealthy services in all ECS clusters::

    $ ecs monitor
    ---- ECS-MYCLUSTER-DEV : 5 services
    [OK]    tools-deployment-prod-1                      desired 1 / running 1
    [KO]    tools-hound-prod-1                           desired 1 / running 0
    [WARN]  tools-jenkins-prod-1                         desired 0 / running 0
    [WARN]  tools-kibana-prod-1                          desired 0 / running 0
    [KO]    tools-sonar-prod-1                           desired 2 / running 1

    ---- ECS-MYCLUSTER-PROD : 5 services
    [OK]    tools-deployment-prod-1                      desired 1 / running 1
    [OK]    tools-hound-prod-1                           desired 1 / running 1
    [WARN]  tools-jenkins-prod-1                         desired 0 / running 0
    [OK]    tools-kibana-prod-1                          desired 2 / running 2
    [OK]    tools-version-prod-1                         desired 2 / running 2

List unhealthy services in ECS clusters that contains 'dev' in their name::

    $ ecs monitor --filter dev
    ---- ECS-MYCLUSTER-DEV : 5 services
    [OK]    tools-deployment-dev-1                       desired 1 / running 1
    [KO]    tools-hound-dev-1                            desired 1 / running 0
    [WARN]  tools-jenkins-dev-1                          desired 0 / running 0
    [WARN]  tools-kibana-dev-1                           desired 0 / running 0
    [KO]    tools-sonar-dev-1                            desired 2 / running 1

Scale service
-------------

The ``scale-service`` command allows you to quickly scale the ``desiredCount`` of
a service in your ECS cluster.

It takes three parameters: the name of the cluster (or its ARN), the name of the
service and the new desired count of tasks for this service.

Usage
~~~~~

::

    Usage: ecs scale-service [OPTIONS] COUNT

      Scale the service to a specific desiredCount.

    Options:
      --cluster TEXT  Name of the ECS cluster  [required]
      --service TEXT  Name of the service  [required]
      --help          Show this message and exit.

::

    $ ecs scale-service --cluster ecs-mycluster-dev --service tools-deployment-dev-1 4
    Updating tools-deployment-dev-1 / desiredCount[1 -> 4] running_count=1

    Service tools-deployment-dev-1 successfully updated with desired_count=4
