import click
from .manager import database
from .webserver.web import get_app


@click.group()
def main():
    pass

default_conn = 'mysql+pymysql://pyuniprot_user:pyuniprot_passwd@localhost/pyuniprot2?charset=utf8'


@main.command()
@click.option('--taxids', default=None, help='List of organisms imported by NCBI taxonomy ID, e.g. 9606,10090,10116 ')
@click.option('--conn', default=default_conn, help='connection string to database, e.g. {}'.format(default_conn))
def update(taxids):
    """Update local UniProt database"""
    if taxids:
        taxids = [int(x) for x in taxids.strip().split(',')]

    database.update(taxids=taxids)


@main.command()
@click.option('--host', default='0.0.0.0', help='Flask host. Defaults to localhost')
@click.option('--port', type=int, help='Flask port. Defaults to 5000')
def web(host, port):
    """Start web application"""
    get_app().run(host=host, port=port)
