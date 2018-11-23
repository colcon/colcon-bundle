# Bundle Format

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
        "installed_packages": ['package=2.11.94']
      },
      "pip3": {
        "installed_packages": ['pypackage1==3.5.0', 'pypackage2>=3.5]
      }
    }
    
signatures.json

    {
      "bundle.tar": {
        "md5": "7e2ca4cc8f282cd4268833a941b9c062",
        "sha1": "b41db935ec6f41e5fe18f880b198e33ebc823831",
        "sha256": "41ba0de4a3b7c6b9371ff069d7dfc8b15348c885c45c4658e8e2ace79b764300"
      }
    }
    
      
### bundle.tar

This contains all the dependencies of the built packages. 
It contains `setup.sh` at the root which can be sourced to add
all the dependencies to the current environment.

When sourcing this `setup.sh` it expects `COLCON_BUNDLE_PREFIX` to
be set to the folder where the contents of `bundle.tar` have 
been extracted.
