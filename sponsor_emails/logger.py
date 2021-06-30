import click

ERROR = click.style("ERROR: ", fg="red", bold=True)
INFO = click.style("INFO: ", fg="blue", bold=True)
WARNING = click.style("WARN: ", fg="yellow", bold=True)


def error(message: str):
    click.echo(ERROR + message)


def info(message: str):
    click.echo(INFO + message)


def warning(message: str):
    click.echo(WARNING + message)
