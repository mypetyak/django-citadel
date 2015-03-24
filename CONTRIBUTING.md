Contributing
============

Below are some notes for a developer interested in contributing to the code base.

##Development Environment:
The easiest way to get started is with [Vagrant](https://www.vagrantup.com/).

Deploy your development virtual machine:

    $ vagrant up
    
This will provision your VM (using puppet) with a postgresql database (`citadel_test`) and a role (username `citadel_test`, password `abcdefghijklmnop`) to get going. Your host directory will now map to the Virtual Machine's `/vagrant` directory.

##Testing:
If you're using Vagrant, ssh into your virtual machine, enter your python virtualenv, and run tests:

    $ vagrant ssh
    $ source /vagrant/env/bin/activate
    $ python /vagrant/runtests.py