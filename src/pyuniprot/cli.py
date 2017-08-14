import click
from .manager import database
from .webserver.web import get_app

@click.group()
def main():
    pass

@main.command()
def update():
    """Update PyUniProt data"""
    database.update()


@main.command()
@click.option('--host', default='0.0.0.0', help='Flask host. Defaults to localhost')
@click.option('--port', type=int, help='Flask port. Defaults to 5000')
def web(host, port):
    get_app().run(host=host, port=port)
