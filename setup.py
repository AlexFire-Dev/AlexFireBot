from setuptools import setup

setup(
    name='AlexFireBot',
    version='0.0',
    description='Бот для AlexFireChat',
    url='https://github.com/AlexFire-Dev/AlexFireBot',
    packages=['AlexFireBot'],
    install_requires=['requests', 'websockets'],
    python_requires='>3.8',
)
