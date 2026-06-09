#!/usr/bin/env python3
import tempfile
from pathlib import PosixPath
from urllib.parse import quote

import click
from anki.collection import Collection, ExportAnkiPackageOptions, DeckIdLimit
from anki.models import NotetypeDict
from anki.notes import Note

from helpers import get_or_create_model, sync_model_templates, sync_model_fields


def _create_text_note(collection: Collection, model: NotetypeDict) -> Note:
    """Generate an example text based note."""
    note = collection.new_note(model)
    note["Title"] = "What is the capital?"
    for idx, (question, answer) in enumerate(
        (
            ("France", "Paris"),
            ("The Netherlands", "Amsterdam"),
            ("Spain", "Madrid"),
            ("UK", "London"),
        )
    ):
        note[f"Q_{idx + 1}"] = question
        note[f"A_{idx + 1}"] = answer
    return note


def _build_inline_image(name: str) -> str:
    path = PosixPath(__file__).parent / "examples" / f"{name}.svg"
    return f'<img src="data:image/svg+xml,{quote(path.read_text())}" />'


def _create_image_note(collection: Collection, model: NotetypeDict) -> Note:
    """Generate an example image based note."""
    note = collection.new_note(model)
    note["Title"] = "Match the top mark to the buoy"

    for idx, (question, answer) in enumerate(
        (
            (
                '<img src="data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20viewBox%3D%270%200%2080%20100%27%3E%3Crect%20x%3D%2720%27%20y%3D%2720%27%20width%3D%2740%27%20height%3D%2730%27%20fill%3D%27black%27/%3E%3Crect%20x%3D%2720%27%20y%3D%2750%27%20width%3D%2740%27%20height%3D%2730%27%20fill%3D%27yellow%27/%3E%3C/svg%3E" />',
                '<img src="data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20viewBox%3D%270%200%2040%2040%27%3E%3Cpath%20d%3D%27M20%205%20L25%2015%20L15%2015%20Z%27%20fill%3D%27black%27/%3E%3Cpath%20d%3D%27M20%2020%20L25%2030%20L15%2030%20Z%27%20fill%3D%27black%27/%3E%3C/svg%3E" />',
            ),
            (
                '<img src="data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20viewBox%3D%270%200%2080%20100%27%3E%3Crect%20x%3D%2720%27%20y%3D%2720%27%20width%3D%2740%27%20height%3D%2720%27%20fill%3D%27red%27/%3E%3Crect%20x%3D%2720%27%20y%3D%2740%27%20width%3D%2740%27%20height%3D%2720%27%20fill%3D%27white%27/%3E%3Crect%20x%3D%2720%27%20y%3D%2760%27%20width%3D%2740%27%20height%3D%2720%27%20fill%3D%27red%27/%3E%3C/svg%3E" />',
                '<img src="data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20viewBox%3D%270%200%2040%2040%27%3E%3Ccircle%20cx%3D%2720%27%20cy%3D%2720%27%20r%3D%2710%27%20fill%3D%27red%27%20stroke%3D%27black%27/%3E%3C/svg%3E" />',
            ),
            (
                None,
                '<img src="data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20viewBox%3D%270%200%2040%2040%27%3E%3Cpath%20d%3D%27M10%2010%20L30%2030%20M30%2010%20L10%2030%27%20stroke%3D%27gold%27%20stroke-width%3D%274%27/%3E%3C/svg%3E" />',
            ),
        )
    ):
        note[f"Q_{idx + 1}"] = question or ""
        note[f"A_{idx + 1}"] = answer
    return note


def _create_package(path: PosixPath, model_name: str) -> None:
    """Create a new package file at the given path."""
    with tempfile.NamedTemporaryFile(suffix="anki2") as f:
        collection = Collection(f.name)

        # Create the model & templates
        model, _ = get_or_create_model(collection, model_name)
        model = sync_model_templates(model)
        model = sync_model_fields(collection, model)
        collection.models.add(model)

        # Create an example deck
        deck_id = collection.decks.id("Drag & Drop Example")

        # Create an example text card
        text_note = _create_text_note(collection, model)
        collection.add_note(text_note, deck_id)

        # Create an example image card
        image_note = _create_image_note(collection, model)
        collection.add_note(image_note, deck_id)

        # Export the package
        collection.export_anki_package(
            out_path=path.absolute().as_posix(),
            options=ExportAnkiPackageOptions(with_scheduling=False, with_media=True, legacy=True),
            limit=DeckIdLimit(deck_id=deck_id),
        )


@click.command()
@click.option(
    "--path",
    type=click.Path(),
    default="drag-and-drop.apkg",
    show_default=True,
    help="Output path for the package file",
)
@click.option(
    "--model-name",
    default="Drag & Drop",
    show_default=True,
    help="Model name to use",
)
def main(path: str, model_name: str) -> None:
    export_path = PosixPath(path)
    print(f"Creating package at {export_path}")
    _create_package(export_path, model_name)


if __name__ == "__main__":
    main()
