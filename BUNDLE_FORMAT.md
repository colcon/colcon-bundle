# Bundle Format - V1

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

# Bundle Format - V2

## Summary

The output of the bundle verb is a tar file containing multiple sub-files

1. version - A file with the version of the bundle file format
1. metadata.tar.gz - A tar archive containing various metadata
1. pad - OPTIONAL used to write the overlays from a fixed offset
1. N *.tar files - These tar archives contain overlay'able contents

** Overlay'able - The top level of each of the archives contains a setup.sh
that can be sources to overlay this archive's contents on top of the 
current environment

### version

Contains a single version number formatted \<major version\>.\<minor version\>. The minor version
will be incremented whenever a backwards compatible change is made. The major version will
be incremented if there is a non-backwards compatible change to the bundle format.

### metadata.tar.gz

All files contained within metadata.tar are formatted as a JSON dictionary. This allows
for backwards compatible additions to any of the files. Order is not guaranteed for this
archive.

**installers.json:**

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
    
**overlays.json:**

Contains overlays to be applied to the envrionment. The unit for offset and
size is bytes.

	{
		"overlays": [
			{
				"file_name": "bundle.tar.gz",
				"sha256": "3c0f891fa2e98c125198afe250054609fd26e7462570ff6d3f6654625627cbf4",
				"offset": 1000,
				"size": 10000
			},
			{
				"file_name": "install.tar.gz",
				"sha256": "650d05f59bc3d19c3871994e0261f7dfe790b050d5baf7c42a2c11f86ee39690",
				"offset": 11000,
				"size": 1000
			}
		]
	}
      
### Overlay archives:

These contain the built packages and dependencies.
At the root each overlay is `setup.sh` which can be sourced to overlay 
the included files on top of the current environment.

Common environment variables modified by a `setup.sh`:

	PATH
	LD_LIBRARY_PATH
	PYTHONPATH

When sourcing each `setup.sh` `COLCON_BUNDLE_PREFIX` should
be set to the folder where the contents of the overlay archive have been extracted. 

See: http://wiki.ros.org/catkin/Tutorials/workspace_overlaying for the original
concept.
