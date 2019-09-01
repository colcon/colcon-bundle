from setuptools import setup

package_name = 'test_py_package'

setup(
    name=package_name,
    version='0.7.0',
    packages=[package_name],
    data_files=[
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    keywords=['ROS'],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
    ],
    description='Test ament_python package',
    license='Apache License, Version 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'run_py_package_tests = test_py_package.test:main',
        ],
    },
)
