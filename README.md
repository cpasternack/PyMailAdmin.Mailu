# v2-admin
Version 2.0 of the mailu admin application built on:
- AdminLTE
- node.js
- sqlAlchemy
- flask
- gunicorn
- python3
- Alpine linux
- OpenSSL
- Docker for x86_64 (amd64)
- probably a whole bunch of other opensource components I haven't remembered to include

Forked from [mailu.io](https://github.com/Mailu/Mailu/tree/master/core/admin) internally. Pushed to github externally as PyMailAdmin.

It's 'Version 2' because I ended up changing so much around the core application.
Internally we use CalVer, and releases are every ~~whenever I get time~~ 6 months

## PyMailAdmin

What it is doing:
- using OpenSSL TLS Self-signed certificates between proxy, mail, and application containers
- using a Docker-centric approach to environmental configuration
- using the latest and greatest versions available
- using Postgresql as a database
- providing me with a management tool for an internal mail system used for development and testing
- running on amd64 servers/virtual machines

What it is not doing:
- using mailu.env configuration file
- using Let's Encrypt certificates
- using the mailu python scripting for containers (application still used)
- using the mailu base containers
- using the mailu jinja templates
- using MariaDB/MySQL/sqlite database
- communicating with services outside of a stand-alone network system (Testing)
- offering any stability above and beyond mailu master branch
- offering any security above and beyond mailu master branch
- running on any other architecture than amd64

Caveat emptor

## Changes:

06/2020:
- multi-multi-stage dockerbuilds
- removed arm architecture
- removed python scripting from container runtime
- added TLS to gunicorn
- renamed project in code
- removed redundant or unused environmental variables in application configuration
- application now does not run as root
- 

07/2020:
- adding CI workflow(s)
- TLS enabled on DB connection

## Contributing

Externally:

If you find this project useful, fork away! 
See the original mailu.io contribution guide in their docs. You should be contributing and working from there.

They seem like a really nice bunch of people, doing a good job for free.

I am not using or providing this as a stand-alone piece. YMMV

Internally:

N.R.

Happy hacking!

### License

MIT

See license/LICENSE.md for mailu.io license
