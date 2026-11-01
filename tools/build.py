#!/usr/bin/env python3
"""Build the seven-page website from editable Markdown and YAML files."""
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import html
import re
import shutil
import sys

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

ROOT = Path(__file__).resolve().parents[1]
NAVIGATION = [
    {'label': 'Home', 'path': '/'},
    {'label': 'Research', 'path': '/research/'},
    {'label': 'Publications', 'path': '/publications/'},
    {'label': 'Projects', 'path': '/projects/'},
    {'label': 'About', 'path': '/about/'},
    {'label': 'Hobbies', 'path': '/hobbies/'},
    {'label': 'Connect', 'path': '/connect/'},
]


def read_document(path):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise ValueError(f'{path.relative_to(ROOT)} must start with a YAML header between --- lines.')
    parts = text.split('---\n', 2)
    if len(parts) != 3:
        raise ValueError(f'{path.relative_to(ROOT)} has no closing --- line.')
    data = yaml.safe_load(parts[1]) or {}
    if not isinstance(data, dict):
        raise ValueError(f'{path.relative_to(ROOT)} needs named settings in its header.')
    data['body'] = parts[2].strip()
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-url', help='Full website URL, including a project subpath if applicable.')
    parser.add_argument('--output', default='_site', help='Output folder, relative to the project root.')
    args = parser.parse_args()
    site = yaml.safe_load((ROOT / 'site.yml').read_text(encoding='utf-8'))
    site_url = (args.site_url or site['url']).rstrip('/')
    parsed = urlsplit(site_url)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError('The site URL must be a full http(s) URL without a query or fragment.')
    origin = f'{parsed.scheme}://{parsed.netloc}'
    base_path = parsed.path.rstrip('/')
    output = ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)

    def url(path):
        if path.startswith('/') and not path.startswith('//'):
            return base_path + path
        return path

    def localize_html(text):
        # Content image/link paths work on both username.github.io and /project/ sites.
        return re.sub(r'(href|src)="(/[^"{}]*)"', lambda m: m[1] + '="' + url(m[2]) + '"', text)

    def rendered(data):
        data['html'] = localize_html(markdown.markdown(data.pop('body'), extensions=['extra', 'sane_lists']))
        return data

    def collection(folder):
        return [rendered(read_document(p)) for p in sorted((ROOT / 'content' / folder).glob('*.md'))]

    topics = sorted(collection('research'), key=lambda item: int(item.get('order', 0)))
    projects = sorted(collection('projects'), key=lambda item: int(item.get('order', 0)))
    papers = sorted(collection('publications'), key=lambda item: (-int(item['year']), int(item.get('order', 0))))
    for item in topics + projects:
        if not re.fullmatch(r'[a-z0-9-]+', str(item.get('id', ''))):
            raise ValueError('Research/project id values may contain only lowercase letters, numbers and hyphens.')
    if len({p['id'] for p in projects}) != len(projects) or len({t['id'] for t in topics}) != len(topics):
        raise ValueError('Research and project id values must be unique within their section.')
    for project in projects:
        template = f'partials/project-{project["id"]}.html'
        project['art_template'] = template if (ROOT / 'templates' / template).exists() else None
        project.setdefault('tags', [])
        project.setdefault('links', [])
        project.setdefault('role', '')
    for paper in papers:
        paper['year'] = str(paper['year'])
        paper.setdefault('venue', paper['year'])
        paper.setdefault('type', 'Paper')
        paper.setdefault('link', '')
        paper['authors_html'] = html.escape(paper['authors']).replace(html.escape(site['name']), '<strong>' + html.escape(site['name']) + '</strong>')
        info = paper['year'] if paper['venue'] == paper['year'] else paper['venue'] + ', ' + paper['year']
        paper['citation'] = f'{paper["authors"]}. {paper["title"]}. {info}.'

    environment = Environment(loader=FileSystemLoader(ROOT / 'templates'), autoescape=select_autoescape(['html']))
    environment.filters['linebreaks'] = lambda text: Markup('<br>'.join(str(escape(text)).splitlines()))
    pages = {}
    for item in NAVIGATION:
        key = 'home' if item['path'] == '/' else item['path'].strip('/')
        pages[key] = rendered(read_document(ROOT / 'content' / f'{key}.md'))
        pages[key]['path'] = item['path']
    common = {
        'site': site, 'navigation': NAVIGATION, 'url': url,
        'research_topics': topics, 'projects': projects,
        'projects_by_id': {p['id']: p for p in projects},
        'publications': papers, 'publication_years': sorted({p['year'] for p in papers}, reverse=True),
        'email_user': site['email'].split('@', 1)[0], 'email_domain': site['email'].split('@', 1)[1],
    }
    for key, page in pages.items():
        context = {**common, 'page': page, 'canonical': origin + url(page['path'])}
        target = output / (key if key != 'home' else '') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(environment.get_template(key + '.html').render(context), encoding='utf-8')

    shutil.copytree(ROOT / 'assets', output / 'assets', dirs_exist_ok=True)
    if (ROOT / 'images').exists():
        for image in (ROOT / 'images').rglob('*'):
            if image.is_file() and image.name != 'README.md':
                destination = output / 'images' / image.relative_to(ROOT / 'images')
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(image, destination)
    (output / '.nojekyll').touch()
    (output / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + origin + url('/sitemap.xml') + '\n')
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + html.escape(origin + url(p['path'])) + '</loc></url>' for p in pages.values()) + '</urlset>'
    (output / 'sitemap.xml').write_text(sitemap)
    # Reuse the homepage's design for the 404 page; the link always points to the configured root.
    error_page = {'browser_title': 'Page not found', 'description': 'Page not found.', 'path': '/404.html'}
    error_template = environment.from_string('{% extends "base.html" %}{% block content %}<header class="page-heading"><span class="eyebrow">404</span><h1>A path less travelled.</h1><p class="lede">This page is not here. Let’s get you back to the homepage.</p></header><a class="button" href="{{ url(\'/\') }}">Back to home →</a>{% endblock %}')
    (output / '404.html').write_text(error_template.render({**common, 'page': error_page, 'canonical': origin + url('/404.html')}))
    print(f'Built {len(pages)} pages at {output} for {site_url}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, yaml.YAMLError) as error:
        sys.exit(f'Content error: {error}')
