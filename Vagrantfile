# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.
  
  config.vm.define "local", primary: true do |local|
    # expected to fix weird error with puppet
    local.vm.hostname = "vagrant.citadel"
    # Every Vagrant virtual environment requires a box to build off of.
    local.vm.box = "precise64"

    # using NFS for speed improvement on OSX
    local.vm.synced_folder "", "/vagrant", :nfs => true

    # download puppet modules
    local.vm.provision :shell do |shell|
      shell.inline = "apt-get update
                      mkdir -p /etc/puppet/modules;
                      puppet module install puppetlabs-postgresql
                      puppet module install stankevich-python"
    end

    # provisioning script
    local.vm.provision :puppet do |puppet|
      # tell puppet privisioner where to look for manifest
      puppet.manifests_path = "puppet"
      puppet.manifest_file = "manifest.pp"
    end

    #local.vm.provision :shell, :path => "vagrant_bootstrap.sh"

    # The url from where the 'config.vm.box' box will be fetched if it
    # doesn't already exist on the user's system.
    local.vm.box_url = "http://files.vagrantup.com/precise64.box"
  
    # Create a forwarded port mapping which allows access to a specific port
    # within the machine from a port on the host machine. In the example below,
    # accessing "localhost:8080" will access port 80 on the guest machine.
    #local.vm.network :forwarded_port, guest: 5000, host: 8080
    local.vm.network :private_network, ip:"192.168.255.2"

    local.vm.provider :virtualbox do |vb|
      # vb.memory = 2048
      # vb.cpus = 1
    end

  end
end
