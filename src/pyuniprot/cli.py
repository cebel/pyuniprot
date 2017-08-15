import click
import re

from .manager import database
from .webserver.web import get_app
from .constants import bcolors


@click.group()
def main():
    pass

example_conn = 'mysql+pymysql://pyuniprot_user:pyuniprot_passwd@localhost/pyuniprot?charset=utf8'


@main.command()
@click.option('-t', '--taxids', default=None, help='List of organisms imported by NCBI taxonomy IDs, '
                                                   'e.g. 9606,10090,10116 ')
@click.option('--conn', default=None, help='connection string to database, e.g. {}'.format(example_conn))
@click.option('--force_download', default=False, help="1 := force to download newest UniProt data\n"
                                                      "0 := take locally stored file even if it's older")
@click.option('--silent', default=0, help="1 := set to 1 if want no output (e.g. cron job)")
def update(taxids, conn, force_download, silent):
    """Update local UniProt database"""
    if not silent:
        warning = "WARNING: Update is very time consuming and can take several\n" \
                  "hours depending which organisms you are importing!\n\n"
        print("{}{}{}".format(bcolors.WARNING,
                              warning,
                              bcolors.ENDC))
        if not taxids:
            note = "Please note that you can restrict import to organisms by\n" \
                       " NCBI taxonomy IDs\n\n"
            example = "Example (human, mouse, rat):\n\t"
            pycommand = "pyuniprot update --taxids 9606,10090,10116\n\n"

            print("{}{}{}{}{}{}{}".format(bcolors.OKBLUE,
                                          note,
                                          example,
                                          bcolors.ENDC,
                                          bcolors.OKGREEN,
                                          pycommand,
                                          bcolors.ENDC))

    if force_download == '1':
        force_download = True
    else:
        force_download = False

    if taxids:
        taxids = [int(taxid.strip()) for taxid in taxids.strip().split(',') if re.search('^ *\d+ *$', taxid)]

    database.update(taxids=taxids, connection=conn, force_download=force_download)


@click.option('--user', default='', help="1 := set to 1 if want no output (e.g. cron job)")
def mysql(user):
    pass

@main.command()
@click.option('--host', default='0.0.0.0', help='Flask host. Defaults to localhost')
@click.option('--port', type=int, help='Flask port. Defaults to 5000')
def web(host, port):
    """Start web application"""
    get_app().run(host=host, port=port)
