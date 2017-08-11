import click
from .manager.database import update
from .webserver.web import get_app

@click.group()
def main():
    pass

@main.command()
def update():
    """Update PyUniProt data"""
    pyuniprot.update()

@main.command()
def web():
    get_app().run()



