#!/usr/bin/env python3
"""Check all generated local links, anchor targets, assets and page headings."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import argparse

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.targets = []
        self.h1 = 0

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag == 'h1':
            self.h1 += 1
        if tag == 'a' and attrs.get('href'):
            self.targets.append(attrs['href'])
        if tag in ('img', 'script') and attrs.get('src'):
            self.targets.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') in ('stylesheet', 'icon'):
            self.targets.append(attrs.get('href', ''))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='_site')
    parser.add_argument('--base-path', default='')
    args = parser.parse_args()
    root = ROOT / args.output
    base = args.base_path.rstrip('/')
    pages = {}
    for file in root.rglob('*.html'):
        data = Page()
        data.feed(file.read_text())
        assert data.h1 == 1, f'{file}: expected one h1'
        assert len(data.ids) == len(set(data.ids)), f'{file}: duplicate id'
        pages[file] = data
    assert len(pages) == 8, f'Expected seven pages plus 404; found {len(pages)}'
    for file, data in pages.items():
        for target in data.targets:
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            path = unquote(parsed.path)
            if path.startswith('/'):
                assert not base or path == base or path.startswith(base + '/'), f'{file}: link missing project prefix: {target}'
                path = path[len(base):] if base else path
                resolved = root / path.lstrip('/')
            elif not path:
                resolved = file
            else:
                resolved = file.parent / path
            if resolved.is_dir():
                resolved = resolved / 'index.html'
            assert resolved.exists(), f'{file}: missing {target}'
            if parsed.fragment and resolved in pages:
                assert unquote(parsed.fragment) in pages[resolved].ids, f'{file}: missing anchor {target}'
    print('Passed: eight pages; internal links, assets, anchor targets, unique IDs and main headings.')


if __name__ == '__main__':
    main()
