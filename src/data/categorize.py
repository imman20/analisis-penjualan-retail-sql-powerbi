"""Penetapan kategori produk berbasis kata kunci pada deskripsi.

Dataset asli tidak memiliki kolom kategori, padahal kategori sangat berguna
untuk filter dashboard dan analisis bauran produk. Aturan di bawah memetakan
kata kunci dalam deskripsi (bahasa Inggris, huruf kapital) ke 9 kategori.
Urutan aturan penting: aturan pertama yang cocok yang dipakai, sehingga kata
kunci yang lebih spesifik (mis. "CHRISTMAS") diletakkan sebelum yang umum
(mis. "DECORATION").

Hasilnya tentu tidak sempurna, tetapi dapat diaudit: setiap kategori punya
daftar kata kunci eksplisit yang bisa ditinjau dan disempurnakan.
"""

from __future__ import annotations

import re

import pandas as pd

# (nama kategori, pola regex kata kunci)
CATEGORY_RULES: list[tuple[str, str]] = [
    ("Christmas & Seasonal", r"CHRISTMAS|XMAS|SANTA|REINDEER|SNOWFLAKE|ADVENT|EASTER|HALLOWEEN|VALENTINE"),
    ("Bags & Accessories", r"\bBAG\b|BAGS|PURSE|WALLET|BACKPACK|UMBRELLA|SCARF|NECKLACE|BRACELET|EARRING|RING\b|HAIR"),
    ("Candles & Lighting", r"CANDLE|T-LIGHT|TEALIGHT|LANTERN|INCENSE|NIGHT LIGHT|LAMP|FAIRY LIGHT"),
    ("Kitchen & Dining", r"MUG|CUP|TEA\b|TEAPOT|TEACUP|BOWL|PLATE|JAR|BOTTLE|CAKE|BAKING|KITCHEN|SPOON|TRAY|JUG|\bTIN\b|LUNCH|NAPKIN|APRON|COASTER|GLASS|OVEN|EGG|CUTLERY|BISCUIT|BREAD|SAUCER"),
    ("Stationery & Gift Wrap", r"CARD|WRAP|PAPER|\bPEN\b|PENS|PENCIL|NOTEBOOK|STICKER|TAPE|ENVELOPE|CRAYON|CHALK|RIBBON|TISSUE|GIFT TAG|BOOK|ERASER|RULER|STAMP"),
    ("Toys & Kids", r"TOY|GAME|PUZZLE|DOLL|KIDS|CHILD|BABY|PLAYHOUSE|SPACEBOY|DINOSAUR|BUBBLE|BALLOON|SKIPPING|PLAYING"),
    ("Garden & Outdoor", r"GARDEN|PLANT|WATERING|FLOWER|HERB|SEED|BIRD|PICNIC|PARASOL|WINDMILL|OUTDOOR"),
    ("Home Decor", r"HEART|SIGN|FRAME|HANGING|DECORATION|ORNAMENT|WREATH|GARLAND|BUNTING|CUSHION|LIGHT|CLOCK|MIRROR|HOOK|CABINET|SHELF|DOOR|BOX|HOLDER|STORAGE|DRAWER|BASKET|VASE|TOWEL|BLANKET|RUG|DOORMAT|CHEST|PHOTO|WALL"),
]
DEFAULT_CATEGORY = "Other"

_COMPILED = [(name, re.compile(pattern)) for name, pattern in CATEGORY_RULES]


def categorize_description(description: str | None) -> str:
    """Mengembalikan kategori untuk satu deskripsi produk."""
    if description is None or (isinstance(description, float) and pd.isna(description)):
        return DEFAULT_CATEGORY
    text = str(description).upper()
    for name, pattern in _COMPILED:
        if pattern.search(text):
            return name
    return DEFAULT_CATEGORY


def categorize_series(descriptions: pd.Series) -> pd.Series:
    """Versi vektor untuk Series deskripsi (memakai cache per nilai unik)."""
    unique_values = descriptions.dropna().unique()
    mapping = {value: categorize_description(value) for value in unique_values}
    return descriptions.map(mapping).fillna(DEFAULT_CATEGORY)
