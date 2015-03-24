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

#postgresql::server::pg_hba_rule{ 'allow citadel_test user passwordless access':
#  description => "Open postgresql for local access to postgres user",
#  type => 'local',
#  database => 'citadel_test',
#  user => 'citadel_test',
#  auth_method => 'trust',
#}

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
