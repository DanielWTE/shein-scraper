import click
from typing import Callable
from dataclasses import dataclass
from scraper.product_urls import collect_product_urls
from scraper.product_details import extract_product_details
from scraper.reviews import collect_reviews

@dataclass
class MenuItem:
    id: int
    title: str
    description: str
    handler: Callable

class ScraperTool:
    def __init__(self):
        self.menu_items = [
            MenuItem(
                1,
                "Product URL Collector",
                "Extract and save product URLs for a specific category",
                collect_product_urls
            ),
            MenuItem(
                2,
                "Product Details Extractor", 
                "Gather and save detailed product information",
                extract_product_details
            ),
            MenuItem(
                3,
                "Review Collector",
                "Download and save product reviews",
                collect_reviews
            )
        ]

@click.group()
def cli():
    pass

@cli.command()
def menu():
    tool = ScraperTool()
    while True:
        click.clear()
        click.secho("=== Web Scraper Tool ===", fg="blue", bold=True)
        click.echo()
        
        for item in tool.menu_items:
            click.secho(f"{item.id}. {item.title}", fg="green")
            click.echo(f"   {item.description}")
            click.echo()
            
        click.echo("0. Exit")
        click.echo()
        
        choice = click.prompt("Select an option", type=int, default=0)
        
        if choice == 0:
            click.echo("Exiting...")
            break
            
        if 1 <= choice <= len(tool.menu_items):
            tool.menu_items[choice-1].handler()
        else:
            click.secho("Invalid option!", fg="red")
            click.pause()

if __name__ == "__main__":
    cli()