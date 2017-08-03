# ECS monitor

ECS monitor lists unhealthy services in your ECS clusters

The script will list the clusters and fetch details about services that are
running in it.

Then it determines if the service is healthy or not:

* the service status must be ACTIVE
* the service must have a non-empty events list
* the service desiredCount equals its runningCount
* the last event message of the service ends with 'has reached a steady state.'

## Usage
```
usage: ecs_monitor.py [-h] [-f FILTER]

List unhealthy services in your ECS clusters.

optional arguments:
  -h, --help            show this help message and exit
  -f FILTER, --filter FILTER
```

List unhealthy services in all ECS clusters:

```
$ ecs_monitor.py
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

```
$ ecs_monitor.py --filter dev
---- ECS-MYCLUSTER-DEV : 9 services
[OK]    tools-deployment-prod-1                      desired 1 / running 1
[KO]    tools-hound-prod-1                           desired 1 / running 0
[WARN]  tools-jenkins-prod-1                         desired 0 / running 0
[WARN]  tools-kibana-prod-1                          desired 0 / running 0
[KO]    tools-sonar-prod-1                           desired 2 / running 1

```
