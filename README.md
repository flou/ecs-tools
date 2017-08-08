# ECS tools

## Monitor

ECS monitor lists unhealthy services in your ECS clusters

The script will list the clusters and fetch details about services that are
running in it.

Then it determines if the service is healthy or not:

* `[OK]` means that its `desiredCount` equals its `runningCount` and it has
  reached a steady state
* `[WARN]` means that its `desiredCount` and its `runningCount` equal 0 but it
  still has reached a steady state
* `[KO]` means that its `desiredCount` does not equal its `runningCount`, or
  that it has not reached a steady state


### Usage

```sh
Usage: ecs monitor [OPTIONS]

  List unhealthy services in your ECS clusters.

Options:
  -f, --filter TEXT  Filter by the name of the ECS cluster
  --help             Show this message and exit.
```

List unhealthy services in all ECS clusters:

```sh
$ ecs monitor
---- ECS-MYCLUSTER-DEV : 9 services
[OK]    tools-deployment-prod-1                      desired 1 / running 1
[KO]    tools-hound-prod-1                           desired 1 / running 0
[WARN]  tools-jenkins-prod-1                         desired 0 / running 0
[WARN]  tools-kibana-prod-1                          desired 0 / running 0
[KO]    tools-sonar-prod-1                           desired 2 / running 1

---- ECS-MYCLUSTER-PROD : 8 services
[OK]    tools-deployment-prod-1                      desired 1 / running 1
[OK]    tools-hound-prod-1                           desired 1 / running 1
[WARN]  tools-jenkins-prod-1                         desired 0 / running 0
[OK]    tools-kibana-prod-1                          desired 2 / running 2
[OK]    tools-version-prod-1                         desired 2 / running 2
```

List unhealthy services in ECS clusters that contains 'dev' in their name:

```sh
$ ecs monitor --filter dev
---- ECS-MYCLUSTER-DEV : 9 services
[OK]    tools-deployment-dev-1                       desired 1 / running 1
[KO]    tools-hound-dev-1                            desired 1 / running 0
[WARN]  tools-jenkins-dev-1                          desired 0 / running 0
[WARN]  tools-kibana-dev-1                           desired 0 / running 0
[KO]    tools-sonar-dev-1                            desired 2 / running 1

```

## Update service

The `update_service` command allows you to quickly update the `desiredCount` of
a service in your ECS cluster.

It takes three parameters: the name of the cluster (or its ARN), the name of the
service and the new desired count of tasks for this service.

### Usage

```sh
Usage: ecs update_service [OPTIONS] COUNT

  Update the DesiredCount of a service in ECS.

Options:
  --cluster TEXT  Name of the ECS cluster  [required]
  --service TEXT  Name of the service  [required]
  --help          Show this message and exit.
```

```sh
$ ecs update_service --cluster ecs-mycluster-dev --service tools-deployment-dev-1 4
Updating tools-deployment-dev-1 / desiredCount[1 -> 4] running_count=1

Service tools-deployment-dev-1 successfully updated with desired_count=4
```
