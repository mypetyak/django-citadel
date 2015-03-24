package { 
  'vim':
    name => 'vim',
    ensure => 'installed';
  'make':
    name => 'make',
    ensure => 'installed';
  'libpq-dev':
    name => 'libpq-dev',
    ensure => 'installed';
}

class { 'postgresql::server': }

postgresql::server::role { 'citadel_test':
  password_hash => postgresql_password('citadel_test', 'abcdefghijklmnop'),
  createdb => true,
}

postgresql::server::db { 'citadel_test':
  user => 'citadel_test',
  password => postgresql_password('citadel_test', 'abcdefghijklmnop'),
}

class { 'python':
  version => 'system',
  pip => true,
  dev => true,
  virtualenv => true,
}

python::virtualenv { '/vagrant/env' :
  ensure => present,
  version => 'system',
  requirements => '/vagrant/requirements.txt',
}
