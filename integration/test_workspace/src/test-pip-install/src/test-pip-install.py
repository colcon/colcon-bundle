#!/usr/bin/env python

import pyquaternion
# From py27_requirements.txt
import packbits

x_rotation = pyquaternion.Quaternion(axis=[1, 0, 0], degrees=10)
y_rotation = pyquaternion.Quaternion(axis=[0, 1, 0], degrees=9)
z_rotation = pyquaternion.Quaternion(axis=[0, 0, 1], degrees=8)

print 'test-pip-install passed...'



