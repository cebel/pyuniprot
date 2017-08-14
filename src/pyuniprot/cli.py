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
def web():
    get_app().run()


