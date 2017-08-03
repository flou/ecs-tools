# ECS monitor

ECS monitor lists unhealthy services in your ECS clusters

The script will list the clusters and fetch details about services that are
running in it.

Then it determines if the service is healthy or not:

* the service status must be ACTIVE
* the service must have a non-empty events list
* the service desiredCount equals its runningCount
* the last event message of the service ends with 'has reached a steady state.'

Usage:

```
# List unhealthy services in all ECS clusters)
$ ecs_monitor.py

# List unhealthy services in ECS clusters that contains 'dev' in their name
$ ecs_monitor.py --filter dev
```
