import click
import re

from .manager import database
from .webserver.web import get_app
from sqlalchemy import create_engine

# try to follow advices on http://click.pocoo.org/5/

example_conn = 'mysql+pymysql://pyuniprot_user:pyuniprot_passwd@localhost/pyuniprot?charset=utf8'

hint_connection_string = [
    "MySQL/MariaDB (strongly recommended):\n\tmysql+pymysql://user:passwd@localhost/database?charset=utf8",
    "PostgreSQL:\n\tpostgresql://user:passwd@localhost/database",
    "MsSQL (pyodbc needed):\n\tmssql+pyodbc://user:passwd@database",
    "SQLite (always works):",
    "- Linux:\n\tsqlite:////absolute/path/to/database.db",
    "- Windows:\n\tsqlite:///C:\\absolute\\path\\to\\database.db",
    "Oracle:\n\toracle://user:passwd@localhost:1521/database\n"
]


def test_connection(conn_str):
    try:
        conn = create_engine(conn_str)
        conn.connect()
        del conn
        click.secho('Connection was sucessfully', fg='green')
    except:
        click.secho('Test was NOT sucessfully', fg='black', bg='red')
        click.echo("\n")
        click.secho('Please use one of the following connection schemas', fg='black', bg='green')
        click.secho('\n\n'.join(hint_connection_string))


@click.group()
@click.version_option()
def main():
    pass


@main.command()
@click.option('-t', '--taxids', default=None, help='List of organisms imported by NCBI taxonomy IDs, '                                                   
                                                   'e.g. 9606,10090,10116 ')
@click.option('-p', '--path', help="path to OBO file")
def obo(path, taxids=None):
    database.export_obo(path)


@main.command()
@click.option('-t', '--taxids', default=None, help='List of organisms imported by NCBI taxonomy IDs, '
                                                   'e.g. 9606,10090,10116 ')
@click.option('-c', '--conn', default=None, help='connection string to database, e.g. {}'.format(example_conn))
@click.option('-f ','--force_download', default=False, help="if is set latest version of UniProt will be downloaded",
              is_flag=True)
@click.option('-s', '--silent', help="True if want no output (e.g. cron job)", is_flag=True)
def update(taxids, conn, force_download, silent):
    """Update local UniProt database"""
    if not silent:
        click.secho("WARNING: Update is very time consuming and can take several\n" \
                  "hours depending which organisms you are importing!\n\n", fg="yellow")

        if not taxids:
            click.echo("Please note that you can restrict import to organisms by\n" \
                       " NCBI taxonomy IDs\n\n")
            click.echo("Example (human, mouse, rat):\n")
            click.secho("\tpyuniprot update --taxids 9606,10090,10116\n\n", fg="green")

    if taxids:
        taxids = [int(taxid.strip()) for taxid in taxids.strip().split(',') if re.search('^ *\d+ *$', taxid)]

    database.update(taxids=taxids, connection=conn, force_download=force_download, silent=silent)


@main.command()
@click.option('-h', '--host', prompt="server name/ IP address database is hosted",
              default='localhost', help="host / servername")
@click.option('-u', '--user', prompt="MySQL/MariaDB user", default='pyuniprot_user', help="MySQL/MariaDB user")
@click.option('-p', '--passwd', prompt="MySQL/MariaDB password", hide_input=True, default='pyuniprot_passwd',
              help="MySQL/MariaDB password to access database")
@click.option('-d', '--db', prompt="database name", default='pyuniprot', help="database name")
@click.option('-c', '--charset', prompt="character set", default='utf8',
              help="character set for mysql connection")
def mysql(host, user, passwd, db, charset):
    """Set MySQL/MariaDB connection"""
    connection_string = database.set_mysql_connection(host=host, user=user, passwd=passwd, db=db, charset=charset)

    test_connection(connection_string)


@main.command()
def version():
    click.echo()


@main.command()
@click.option('--host', default='0.0.0.0', help='Flask host. Defaults to localhost')
@click.option('--port', type=int, help='Flask port. Defaults to 5000')
def web(host, port):
    """Start web application"""
    get_app().run(host=host, port=port)


@main.command()
@click.option('-c', '--connection', prompt="connection string", help="valid SQLAlchemy connection strings")
@click.option('-wct', '--without_connection_test', help="check", is_flag=False)
def connection(connection, without_connection_test):
    """Set MySQL/MariaDB connection"""
    database.set_connection(connection=connection)

    if not without_connection_test:
        test_connection(connection)


