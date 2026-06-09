from pathlib import PosixPath

from anki.collection import Collection
from anki.models import NotetypeDict


def _load_file(file_name: str) -> str:
    path = PosixPath(__name__).parent.parent / "template" / file_name
    return path.read_text()


def get_or_create_model(collection: Collection, model_name: str) -> tuple[NotetypeDict, bool]:
    """Fetch or create a new model with a given name."""
    if model := collection.models.by_name(model_name):
        return model, False

    model = collection.models.new(model_name)
    collection.models.add_template(model, collection.models.new_template(model_name))
    return model, True


def sync_model_templates(model: NotetypeDict) -> NotetypeDict:
    """Update a model with our latest templates."""
    model["css"] = _load_file("style.css")
    model["tmpls"][0]["qfmt"] = _load_file("front.html")
    model["tmpls"][0]["afmt"] = _load_file("back.html")
    return model


def sync_model_fields(collection: Collection, model: NotetypeDict) -> NotetypeDict:
    """Update a model with our expected fields."""
    expected_fields = ["Title", "Question", "Sources"] + [f for n in range(1, 11) for f in (f"Q_{n}", f"A_{n}")]
    existing_fields = {f["name"] for f in model["flds"]}

    for field_name in expected_fields:
        if field_name not in existing_fields:
            collection.models.add_field(model, collection.models.new_field(field_name))

    return model
