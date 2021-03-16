import setuptools

setuptools.setup(
    name='sleepcounter-hardware-a',
    version='2.2.7',
    packages=setuptools.find_namespace_packages(include=["sleepcounter.*"]),
    install_requires=[
        # third-party...
        'max7219',
        'stage>=0.3.0',
        # project specific...
        'sleepcounter-core',
    ],
    entry_points={
        'console_scripts':
            ['sleepcounter=sleepcounter.hardware_a.__main__:main'],
    }
)
