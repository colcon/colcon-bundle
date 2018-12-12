# Bundle Format V1

## Summary

The output of the bundle verb is a tar'd and gzip'd file containing the following:

1. version - A file with the version of the bundle file format
1. metadata.tar - A tar archive containing various metadata
1. bundle.tar - A tar archive containing the filesystem bundle

### version

Contains a single version number formatted \<major version\>.\<minor version\>. The minor version
will be incremented whenever a backwards compatible change is made. The major version will
be incremented if there is a non-backwards compatible change to the bundle format.

### metadata.tar

All files contained within metadata.tar are formatted as a JSON dictionary. This allows
for backwards compatible additions to any of the files. Order is not guaranteed for this
archive.

installers.json

    {
	  "apt": {
		"installed_packages": [
		  {
			"version": "2.26.1",
			"name": "pacakge1"
		  },
		  {
			"version": "1.0.6-8",
			"name": "package2"
		  }
		]
	  }
	  "pip3": {
		"installed_packages": [
		  {
			"version": "1.11.13",
			"name": "package1"
		  },
		  {
			"version": "1.8.3",
			"name": "package2"
		  }
		]
	  }
    }
      
### bundle.tar

This contains the built packages and all of their dependencies.
It contains `setup.sh` at the root which can be sourced to add
all the dependencies to the current environment.

When sourcing this `setup.sh` it expects `COLCON_BUNDLE_PREFIX` to
be set to the folder where the contents of `bundle.tar` have 
been extracted.
