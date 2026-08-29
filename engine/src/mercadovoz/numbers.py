from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, InvalidOperation

SMALL = {
    "cero": 0,
    "un": 1,
    "uno": 1,
    "una": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
    "diez": 10,
    "once": 11,
    "doce": 12,
    "trece": 13,
    "catorce": 14,
    "quince": 15,
    "dieciseis": 16,
    "diecisiete": 17,
    "dieciocho": 18,
    "diecinueve": 19,
    "veinte": 20,
    "veintiuno": 21,
    "veintidos": 22,
    "veintitres": 23,
    "veinticuatro": 24,
    "veinticinco": 25,
    "veintiseis": 26,
    "veintisiete": 27,
    "veintiocho": 28,
    "veintinueve": 29,
}
TENS = {
    "treinta": 30,
    "cuarenta": 40,
    "cincuenta": 50,
    "sesenta": 60,
    "setenta": 70,
    "ochenta": 80,
    "noventa": 90,
}
HUNDREDS = {"cien": 100, "ciento": 100}
NUMBER_WORDS = set(SMALL) | set(TENS) | set(HUNDREDS) | {"y"}


def strip_accents(text: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )


def parse_number_words(words: list[str]) -> Decimal | None:
    if not words or any(word not in NUMBER_WORDS for word in words):
        return None
    total = 0
    current = 0
    meaningful = False
    for word in words:
        if word == "y":
            continue
        meaningful = True
        if word in HUNDREDS:
            current += HUNDREDS[word]
        elif word in TENS:
            current += TENS[word]
        else:
            current += SMALL[word]
    return Decimal(total + current) if meaningful else None


def replace_number_words(text: str) -> str:
    tokens = re.findall(r"\d+(?:[.,]\d+)?|[a-zñ]+|\$|[^\w\s]", text)
    output: list[str] = []
    index = 0
    while index < len(tokens):
        if tokens[index] not in NUMBER_WORDS or tokens[index] == "y":
            output.append(tokens[index])
            index += 1
            continue
        end = index
        while end < len(tokens) and tokens[end] in NUMBER_WORDS:
            end += 1
        words = tokens[index:end]
        while words and words[-1] == "y":
            words.pop()
            end -= 1
        value = parse_number_words(words)
        if value is None:
            output.append(tokens[index])
            index += 1
        else:
            output.append(str(int(value)))
            index = end
    return " ".join(output)


def to_decimal(value: str | int | float | Decimal | None) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value).replace(",", "."))
    except InvalidOperation:
        return None

