#!/usr/bin/env python3
"""Literal quotation from an explicit UTF-8 source; no private transcript access."""
from pathlib import Path
import argparse
import hashlib
import re


def collapse(text):
    return re.sub(r'\s+', ' ', text).strip()


def source_path(workspace, arquivo):
    if not workspace or not arquivo:
        raise ValueError('workspace e arquivo são obrigatórios')
    root = Path(workspace).resolve()
    path = (root / arquivo).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Fonte fora do workspace autorizado')
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _parse_range(value):
    if re.fullmatch(r'\d+-\d+', value.strip()):
        start, end = map(int, value.split('-'))
        if end < start:
            raise ValueError('Faixa de itens invertida')
        return list(range(start, end + 1))
    if not re.fullmatch(r'\d+(?:[ ,]+\d+)*', value.strip()):
        raise ValueError('Faixa de itens inválida')
    return [int(x) for x in re.split(r'[ ,]+', value.strip())]


def _extract_span(text, trecho):
    match = re.fullmatch(r'de\s+"(.+?)"\s+at[eé]\s+"(.+?)"', trecho.strip(), re.S | re.I)
    if not match:
        raise ValueError('Use trecho: de "início" ate "fim"')
    start, end = map(collapse, match.groups())
    if not start or not end or text.count(start) != 1 or text.count(end) != 1:
        raise LookupError('Âncora ausente ou ambígua; use âncoras únicas')
    i, j = text.index(start), text.index(end)
    if j < i:
        raise LookupError('Âncoras invertidas')
    return text[i:j + len(end)]


def resolve_file(workspace, arquivo, sha256, itens=None, trecho=None):
    path = source_path(workspace, arquivo)
    if not sha256 or not re.fullmatch(r'[a-fA-F0-9]{64}', sha256):
        raise ValueError('sha256 válido é obrigatório')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha256.lower():
        raise ValueError('SHA-256 divergente: fonte alterada desde a captura')
    text = raw.decode('utf-8-sig')
    if itens:
        parts = re.split(r'(?m)^\s*(\d+)\.\s+', text)
        pairs = [(int(parts[i]), parts[i+1]) for i in range(1, len(parts)-1, 2)]
        if len({n for n, _ in pairs}) != len(pairs):
            raise LookupError('Numeração repetida; delimite a fonte antes de recortar')
        mapping = dict(pairs)
        nums = _parse_range(itens)
        if len(set(nums)) != len(nums):
            raise ValueError('Itens repetidos')
        if any(n not in mapping for n in nums):
            raise LookupError('Item não encontrado na fonte')
        text = ' '.join(f'{n}. {collapse(mapping[n])}' for n in nums)
    text = collapse(text)
    if trecho:
        text = _extract_span(text, trecho)
    if not text:
        raise ValueError('Fonte ou recorte vazio')
    return text, str(path)


def find_grifo(texto, grifo):
    value = collapse(grifo)
    if not value or texto.count(value) != 1:
        raise LookupError('Grifo ausente ou ambíguo')
    start = texto.index(value)
    return start, start + len(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hash', dest='hash_file')
    parser.add_argument('--workspace')
    parser.add_argument('--arquivo')
    parser.add_argument('--sha256')
    parser.add_argument('--itens')
    parser.add_argument('--trecho')
    args = parser.parse_args()
    if args.hash_file:
        print(digest(args.hash_file))
    else:
        text, source = resolve_file(args.workspace, args.arquivo, args.sha256, args.itens, args.trecho)
        print(f'[fonte: {source}]\n{text}')


if __name__ == '__main__':
    main()
