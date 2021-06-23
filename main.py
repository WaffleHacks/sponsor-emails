import click
from pathlib import Path

from sponsor_emails import load_config


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
        ctx.ensure_object(dict)
        ctx.obj["CONFIG"] = load_config(config_path)


if __name__ == "__main__":
    main()
