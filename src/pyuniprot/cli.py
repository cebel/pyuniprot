import click
from .webserver.web import get_app


@click.group()
def main():
    pass


@main.command()
def web():
    get_app().run()



