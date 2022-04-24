from setuptools import setup

setup(
    name='Heikin-Ashi-Scanner',
    version='1.0.1',
    packages=[''],
    python_requires='>=3.7, <4',
    install_requires=['pandas', 'numpy', 'argparse', 'stockstats', 'ta', 'requests', 'prettytable', 'mysql', 'wallstreet'],
    url='https://github.com/Koshban/{name}',
    license='https://creativecommons.org/licenses/by-sa/4.0/',
    author='kaushik and Sid',
    author_email='kaushik.banerjee77@gmail.com',
    description='heikin-ashi scanner'
)
