Static analysis task
====================

This task is using csmock for performing static analysis on provided source RPM.

## Installation

[Taskotron stuff](http://libtaskotron.readthedocs.org/en/latest/quickstart.html)

```
yum install libtaskotron
```

Task's stuff

```
yum install csmock csmock-plugin-{clang,cppcheck}
```

## Usage

```
runtask -d -i <nvr> -t koji_build ./task.yml
```

