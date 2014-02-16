from setuptools import setup, find_packages
setup(
        name = "lite2j",
        version = "0.1",
        description = "Dump sqlite files as json",
        author = "John Gerlock",
        author_email = "john.gerlock@gmail.com",
        url = "http://github.com/john-g-g/lite2j",
        entry_points={
            'console_scripts': ['lite2j=lite2j:main',],
                },
        packages = find_packages(),

)
