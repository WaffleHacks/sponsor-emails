import click
from pathlib import Path
from pydantic import ValidationError
from sys import exit

from sponsor_emails import Config, load_config, tests


def error(message: str):
    """
    Display an error message
    :param message: the message to display
    """
    click.echo(click.style("ERROR: ", fg="red", bold=True) + message)


@click.group(
    name="sponsor-emails",
    help="Automate sending sponsorship emails using Google Docs, Google Sheets, and MailGun",
)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
        allow_dash=False,
        path_type=Path,
    ),
    help="Configuration file to load",
    default="./config.json",
)
@click.pass_context
def main(ctx: click.Context, config_path: Path):
    # Send help if no subcommand
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

    else:
        try:
            ctx.obj = load_config(config_path)
        except ValidationError as e:
            error("failed to load configuration")

            for err in e.errors():
                location = ".".join(err["loc"])
                styled = click.style(location, fg="yellow")

                message = err["msg"]

                click.echo(f"\t{styled}: {message}")

            exit(1)


@main.command(help="Check that the configuration is valid")
@click.pass_obj
def validate(cfg: Config):
    for test in tests.METHODS:
        click.echo(test(cfg))


if __name__ == "__main__":
    main()
