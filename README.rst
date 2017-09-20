ECS tools
=========

.. image:: https://img.shields.io/pypi/v/ecs-tools.svg
    :target: https://pypi.python.org/pypi/ecs-tools

.. image:: https://img.shields.io/pypi/l/ecs-tools.svg
    :target: https://pypi.python.org/pypi/ecs-tools

.. image:: https://img.shields.io/pypi/wheel/ecs-tools.svg
    :target: https://pypi.python.org/pypi/ecs-tools

.. image:: https://img.shields.io/pypi/pyversions/ecs-tools.svg
    :target: https://pypi.python.org/pypi/ecs-tools

-------------------------------------

Installation
------------

::

    pip install ecs-tools

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
    123456789012.dkr.ecr.us-east-1.amazonaws.com/acme/srv-deployment:1.0.3-dev

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
    [KO]    tools-hound-dev-1                            running 0/1 (hound-dev:75)
    [WARN]  tools-jenkins-dev-1                          running 0/0 (jenkins-dev:247)
    [WARN]  tools-kibana-dev-1                           running 0/0 (srv-kibana:55)
    [KO]    tools-sonar-dev-1                            running 2/1 (srv-sonar:923)

    ---- ECS-MYCLUSTER-PROD : 5 services
    [WARN]  tools-jenkins-prod-1                         running 0/0 (jenkins-prod:247)


By default ``ecs monitor`` only shows services that are ``KO`` or ``WARN``, use
the ``-a/--all`` option to list all services.

List all services in ECS clusters that contains 'dev' in their name::

    $ ecs monitor --all --filter dev
    ---- ECS-MYCLUSTER-DEV : 5 services
    [OK]    tools-deployment-dev-1                       running 1/1 (srv-deployment-dev:3)
    [KO]    tools-hound-dev-1                            running 0/1 (hound-dev:75)
    [WARN]  tools-jenkins-dev-1                          running 0/0 (jenkins-dev:247)
    [WARN]  tools-kibana-dev-1                           running 0/0 (srv-kibana:55)
    [KO]    tools-sonar-dev-1                            running 2/1 (srv-sonar:923)

You can also get more information by using the ``-l/--long`` option::

    $ ecs monitor --long --filter prod
    ---- ECS-MYCLUSTER-PROD : 5 services
    [WARN]  tools-jenkins-prod-1                         running 0/0 (jenkins-prod:142)
    Name:         jenkins
    Docker image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/acme/jenkins:2.77-custom
    Memory:       1024
    CPU:          512
    Ports:        ->8080
    Environment:
        JAVA_OPTS: -Dhudson.footerURL=http://mycompany.com
        JENKINS_OPTS: --prefix=/jenkins
        JENKINS_SLAVE_AGENT_PORT: 50001
        PLATFORM: prod
        PROJECT: acme

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
