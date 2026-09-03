#!/usr/bin/env python3
"""
fix_site.py — repairs and enhances the HTML of mahtaakhyani.github.io.

Order matters: structural repairs (unclosed tags) run BEFORE anything that
inserts new markup, otherwise insertions land inside a broken element.

Rules:
  * Never deletes or invents page content. Only repairs broken references and
    adds technical / accessibility scaffolding.
  * Idempotent: safe to run repeatedly.
"""
import glob
import os
import re
import sys
from collections import Counter

SITE = "https://mahtaakhyani.github.io/"
LOG = Counter()


def note(key, n=1):
    if n:
        LOG[key] += n


# Pages written as if they sat one directory deeper: every "../" escapes root.
ORPHAN_PAGES = {
    "electrical-compass.html",
    "line-following-robot.html",
    "wastewater-treatment-by-algae.html",
}

# Editor leftovers: keep the files, but keep them out of search results.
NOINDEX_PAGES = {
    "Blog-Template.html",
    "Mahta-Akhyani_1525372.html",
    "Projects0.html",
}

EXTRACURRICULAR = ["Video Creating", "Drawing", "Playing Music",
                   "Handy-Crafts", "Theatre Club", "Volunteering"]

LINK_FIXES = [
    (r'(href=")Phantom\.html(")', r'\1brain-phantom-synthesis.html\2'),
    (r'(href=")electrical-compass-awarded\.html(")', r'\1electrical-compass.html\2'),
    (r'(href=")Compass\.html(")', r'\1electrical-compass.html\2'),
    (r'(href=")FFR\.html(")', r'\1firefighting-robot.html\2'),
    (r'(href=")LFR\.html(")', r'\1line-following-robot.html\2'),
    (r'(href=")WWT\.html(")', r'\1wastewater-treatment-by-algae.html\2'),
    (r'(href=")blog/slam-capable-robot\.html(")', r'\1SLAM.html\2'),
    (r'(href|src)="/(nicepage\.css|jquery\.js|nicepage\.js|Projects\.html|SLAM\.html|Certificates\.html)"',
     r'\1="\2"'),
    (r'Extracricular', r'Extracurricular'),
]


# ===========================================================================
# STAGE 1 — structural repairs
# ===========================================================================

def close_jsonld_script(html):
    """CRITICAL. Four pages opened <script type="application/ld+json"> and
    never closed it, so the browser swallowed the whole rest of the document
    as script data and rendered a blank page."""
    i = html.find('<script type="application/ld+json">')
    if i == -1 or html.find('</script>', i) != -1:
        return html
    # The closing brace may be indented, so match the first line that is
    # nothing but whitespace and a '}'.
    m = re.compile(r'\n[ \t]*\}[ \t]*(?=\n|$)').search(html, i)
    if not m:
        return html
    end = m.end()
    note("unclosed JSON-LD <script> closed (page rendered blank)")
    return html[:end] + '</script>' + html[end:]


def close_head(html):
    if '</head>' in html:
        return html
    m = re.search(r'<body\b', html)
    if not m:
        return html
    note("missing </head> added")
    return html[:m.start()] + '</head>\n' + html[m.start():]


def fix_malformed_attributes(html):
    # <script ... src="jquery.js" "="" defer=""> — a stray empty attribute.
    html, n = re.subn(r'\s+"=""\s+', ' ', html)
    note("malformed empty attribute removed", n)

    # Stray glyph inside an attribute name, e.g. aria-selected<U+2642>="false".
    html, n = re.subn(
        r'\b(aria-[a-z]+|data-[a-z-]+|role|class|id|href|src|alt|title)'
        r'[^\sa-z0-9="\'>/-]+="', r'\1="', html)
    note("stray character in attribute name removed", n)

    # Two attributes run together with no space: class="x"data-foo="y".
    # Only fires when the following name is a known attribute, so that quoted
    # values containing '=' (viewport, URLs) are never touched.
    html, n = re.subn(
        r'(<[a-zA-Z][^<>]*?")((?:data-[a-z-]+|aria-[a-z]+|class|style|id|href|src|'
        r'alt|title|role|type|rel|width|height|loop|muted|defer|async)=")',
        r'\1 \2', html)
    note("missing space between attributes", n)
    return html


def fix_stray_closing_tags(html):
    html, n = re.subn(r'</h1>(\s*</span>)', r'\1', html)
    note("stray </h1> removed", n)
    html, n = re.subn(r'(<h3\b[^>]*>(?:(?!</h3>|<h3\b).)*?)</h1>', r'\1</h3>',
                      html, flags=re.S)
    note("mismatched </h1> corrected to </h3>", n)
    html, n = re.subn(r'</p>(\s*)</p>', r'</p>', html)
    note("duplicate </p> removed", n)
    return html


def fix_menu_nesting(html):
    """The "School Years" submenu never closed its popup <div> or its <li>,
    so "Extracurricular" was nested inside it; a surplus </ul> then closed the
    mega-menu container early."""
    html, n = re.subn(
        r'(</li>\s*</ul>\s*)(<li class="u-nav-item"><a class="u-button-style '
        r'u-nav-link" href="#" style="font-weight: 700;">Extrac(?:ri|urri)cular</a>)',
        r'\1</div>\n</li>\n\2', html)
    note("School Years submenu closed", n)

    html, n = re.subn(r'</ul>\s*</ul>\s*</div>\s*</li></ul>',
                      '</ul>\n</div>\n</li></ul>', html)
    note("surplus </ul> removed", n)
    return html


def fix_orphaned_tab_link(html):
    """A tab <a> had escaped its <li> wrapper, leaving an empty list item."""
    html, n = re.subn(
        r'(<ul[^>]*class="[^"]*u-tab-list[^"]*"[^>]*>(?:(?!</ul>).)*?)'
        r'(<a\b[^>]*class="[^"]*u-tab-link[^"]*"[^>]*>.*?</a>)\s*\n?\s*'
        r'<li class="u-tab-item" role="presentation">\s*\n?\s*</li>',
        lambda m: m.group(1) + '<li class="u-tab-item" role="presentation">\n  '
                  + m.group(2) + '\n</li>',
        html, flags=re.S)
    note("orphaned tab link re-nested", n)
    return html


def ensure_lang(html):
    if re.search(r'<html\b[^>]*\blang=', html):
        return html
    note("lang attribute added")
    return re.sub(r'<html\b', '<html lang="en"', html, count=1)


# ===========================================================================
# STAGE 2 — link repairs
# ===========================================================================

def fix_orphan_paths(html, fname):
    if fname not in ORPHAN_PAGES:
        return html
    before = html
    html = html.replace('"../mailto:', '"mailto:')
    html = re.sub(r'((?:href|src)=")\.\./', r'\1', html)
    if html != before:
        note("orphan ../ paths repaired: " + fname)
    return html


def fix_links(html):
    for pat, rep in LINK_FIXES:
        html, n = re.subn(pat, rep, html)
        note("link fix: " + pat[:38], n)
    return html


def fix_extracurricular_targets(html):
    """The Extracurricular submenu items each pointed at an unrelated robotics
    page. Retarget them to the portfolio — but only inside the nav popup, never
    the tab strip on Projects.html, which uses the same labels."""
    def in_popup(block):
        for label in EXTRACURRICULAR:
            pat = (r'(<a\b[^>]*?class="[^"]*u-nav-link[^"]*"[^>]*?href=")[^"]*?'
                   r'("[^>]*?>\s*' + re.escape(label) + r'\s*</a>)')
            block, n = re.subn(pat, r'\1Projects.html\2', block)
            note("extracurricular nav link retargeted", n)
        return block

    return re.sub(r'<div class="level-3 u-nav-popup">.*?</ul>',
                  lambda m: in_popup(m.group(0)), html, flags=re.S)


def restore_tab_hrefs(html):
    """A tab link's href must be its own panel id."""
    def tab(m):
        tag = m.group(0)
        ac = re.search(r'aria-controls="([^"]+)"', tag)
        if not ac:
            return tag
        want = '#' + ac.group(1)
        h = re.search(r'href="([^"]*)"', tag)
        if h and h.group(1) == want:
            return tag
        note("tab link href aligned with its panel")
        if h:
            return tag.replace(h.group(0), 'href="%s"' % want)
        return tag[:-1].rstrip() + ' href="%s">' % want

    return re.sub(r'<a\b[^>]*class="[^"]*u-tab-link[^"]*"[^>]*>', tab, html)


def fix_contact_nav(html):
    mail = ('mailto:Mahtaakhyani@gmail.com?subject='
            'Contacting%20Mahta%20Akhyani%20to%20offer%20a%20position')
    html, n = re.subn(
        r'(<a\b[^>]*?)href="#"([^>]*?>)(\s*)Contact(\s*)</a>',
        lambda m: '%shref="%s"%s%sContact%s</a>' % (m.group(1), mail, m.group(2),
                                                    m.group(3), m.group(4)),
        html)
    note("Contact nav link wired to email", n)
    return html


def wire_dead_nav_item(html):
    html, n = re.subn(
        r'<a class="u-button-style u-nav-link">Electrical Compass \(Awarded\)</a>',
        '<a class="u-button-style u-nav-link" href="electrical-compass.html">'
        'Electrical Compass (Awarded)</a>', html)
    note("dead mobile nav item given a destination", n)
    return html


def drop_blank_target_on_internal(html):
    def rep(m):
        tag = m.group(0)
        h = re.search(r'href="([^"]*)"', tag)
        if not h:
            return tag
        v = h.group(1)
        if re.match(r'^(https?:|mailto:|tel:|//)', v) or not v.endswith('.html'):
            return tag
        note("internal target=_blank removed")
        return re.sub(r'\s*target="_blank"', '', tag)

    return re.sub(r'<a\b[^>]*target="_blank"[^>]*>', rep, html)


def harden_external_links(html):
    def rep(m):
        tag = m.group(0)
        rel = re.search(r'\brel="([^"]*)"', tag)
        if rel:
            vals = set(rel.group(1).split())
            if {'noopener', 'noreferrer'} <= vals:
                return tag
            vals |= {'noopener', 'noreferrer'}
            note("rel=noopener noreferrer added")
            return tag.replace(rel.group(0), 'rel="%s"' % ' '.join(sorted(vals)))
        note("rel=noopener noreferrer added")
        return tag[:-1].rstrip() + ' rel="noopener noreferrer">'

    return re.sub(r'<a\b[^>]*target="_blank"[^>]*>', rep, html)


def comment_dead_stylesheet(html):
    if 'Post-Template.css is not present' in html:
        return html  # already commented out on a previous run
    pat = r'(\s*)<link([^>]*)href="(?:\.\./)?Post-Template\.css"([^>]*)>'
    if not re.search(pat, html):
        return html
    note("dead stylesheet reference commented out")
    return re.sub(pat,
                  r'\1<!-- Post-Template.css is not present in this repository; '
                  r'restore the file and uncomment to re-enable. '
                  r'<link\2href="Post-Template.css"\3> -->', html)


# ===========================================================================
# STAGE 3 — head, metadata, performance, accessibility
# ===========================================================================

def font_display_swap(html):
    def rep(m):
        url = m.group(2)
        if 'display=swap' in url:
            return m.group(0)
        note("font-display=swap added")
        return m.group(1) + url + '&amp;display=swap' + m.group(3)

    return re.sub(r'(href=")(https://fonts\.googleapis\.com/css\?family=[^"]+)(")',
                  rep, html)


def fix_jsonld(html):
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if not m or '"@type": "Organization"' not in m.group(1):
        return html
    urls = [u for u in re.findall(r'"((?:https?://|mailto:)[^"]+)"', m.group(1))
            if 'schema.org' not in u]
    seen = []
    for u in urls:
        if u not in seen:
            seen.append(u)
    block = ('<script type="application/ld+json">{\n'
             '\t"@context": "https://schema.org",\n'
             '\t"@type": "Person",\n'
             '\t"name": "Mahta Akhyani",\n'
             '\t"url": "%s",\n'
             '\t"image": "%simages/Mahta.svg",\n'
             '\t"sameAs": [\n\t\t\t%s\n\t]\n}</script>'
             % (SITE, SITE, ',\n\t\t\t'.join('"%s"' % u for u in seen)))
    note("JSON-LD corrected from Organization to Person")
    return html.replace(m.group(0), block, 1)


def upgrade_head(html, fname, title):
    head_end = html.find('</head>')
    if head_end == -1:
        return html
    head = html[:head_end]
    add = []

    canon_page = 'index.html' if fname in ('index.html', 'Mahta-Akhyani.html') else fname
    canon = SITE if canon_page == 'index.html' else SITE + canon_page

    if re.search(r'<link[^>]*rel="canonical"', head):
        html = re.sub(r'<link[^>]*rel="canonical"[^>]*>',
                      '<link rel="canonical" href="%s">' % canon, html, count=1)
        note("canonical URL repaired")
    else:
        add.append('<link rel="canonical" href="%s">' % canon)
        note("canonical URL added")

    if 'property="og:url"' in head:
        html = re.sub(r'<meta[^>]*property="og:url"[^>]*>',
                      '<meta property="og:url" content="%s">' % canon, html, count=1)
        note("og:url made absolute")
    else:
        add.append('<meta property="og:url" content="%s">' % canon)

    m = re.search(r'<meta[^>]*property="og:image"[^>]*content="([^"]+)"[^>]*>', head)
    if m and not m.group(1).startswith('http'):
        html = html.replace(m.group(0),
                            '<meta property="og:image" content="%s%s">' % (SITE, m.group(1)), 1)
        note("og:image made absolute")

    t = title or 'Mahta Akhyani'
    if 'property="og:type"' not in head:
        add.append('<meta property="og:type" content="website">')
    if 'property="og:site_name"' not in head:
        add.append('<meta property="og:site_name" content="Mahta Akhyani">')
    if 'name="twitter:card"' not in head:
        add.append('<meta name="twitter:card" content="summary_large_image">')
        add.append('<meta name="twitter:title" content="%s">' % t)
        note("Twitter card metadata added")
    if 'name="author"' not in head:
        add.append('<meta name="author" content="Mahta Akhyani">')
    if 'name="theme-color"' not in head:
        add.append('<meta name="theme-color" content="#ffbb00">')
    if 'name="color-scheme"' not in head:
        add.append('<meta name="color-scheme" content="light">')
    if 'name="robots"' not in head:
        if fname in NOINDEX_PAGES:
            add.append('<meta name="robots" content="noindex, follow">')
            note("noindex applied to editor leftover")
        else:
            add.append('<meta name="robots" content="index, follow, max-image-preview:large">')
    if 'rel="icon"' not in head:
        add.append('<link rel="icon" href="images/Mahta.svg" type="image/svg+xml">')
        add.append('<link rel="apple-touch-icon" href="images/Mahta.svg">')
        note("favicon added")
    if 'rel="preconnect" href="https://fonts.googleapis.com"' not in head:
        add.insert(0, '<link rel="preconnect" href="https://fonts.googleapis.com">')
        add.insert(1, '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
        note("font preconnect hints added")
    if 'assets/enhancements.css' not in head:
        add.append('<link rel="stylesheet" href="assets/enhancements.css" media="screen">')
    if 'assets/enhancements.js' not in head:
        add.append('<script src="assets/enhancements.js" defer></script>')
        note("enhancement layer linked")

    if add:
        html = html.replace('</head>', '    ' + '\n    '.join(add) + '\n</head>', 1)
    return html


def media_perf(html):
    imgs = list(re.finditer(r'<img\b[^>]*>', html))
    out, last = [], 0
    for i, m in enumerate(imgs):
        tag = m.group(0)
        out.append(html[last:m.start()])
        if 'loading=' not in tag and 'decoding=' not in tag:
            if i == 0:
                tag = tag[:-1].rstrip() + ' decoding="async" fetchpriority="high">'
            else:
                tag = tag[:-1].rstrip() + ' loading="lazy" decoding="async">'
                note("image lazy-loaded")
        out.append(tag)
        last = m.end()
    out.append(html[last:])
    html = ''.join(out)

    def vid(m):
        tag = m.group(0)
        if 'preload=' in tag:
            return tag
        note("video preload deferred")
        extra = ' preload="none"'
        if 'playsinline' not in tag:
            extra += ' playsinline'
        return tag[:-1].rstrip() + extra + '>'

    return re.sub(r'<video\b[^>]*>', vid, html)


def label_blank_alt_thumbnails(html):
    def rep(m):
        note("thumbnail alt text filled from post title")
        slug = os.path.splitext(os.path.basename(m.group(2)))[0]
        return m.group(1) + 'alt="%s"' % slug.replace('-', ' ').replace('_', ' ').title()

    # The <img> must sit inside this same anchor — an unconstrained .*? would
    # reach across the document and relabel an unrelated icon.
    return re.sub(r'(<a class="u-post-header-link" href="([^"]+)">'
                  r'(?:(?!</a>).)*?<img[^>]*?)alt=""',
                  rep, html, flags=re.S)


def add_skip_link(html):
    if 'class="skip-link"' in html:
        return html
    m = re.search(r'<body\b[^>]*>', html)
    if not m:
        return html
    note("skip-to-content link added")
    return (html[:m.end()] +
            '\n<a class="skip-link" href="#main-content">Skip to main content</a>' +
            html[m.end():])


def add_main_landmark(html):
    if 'id="main-content"' in html:
        return html
    m = re.search(r'</header>', html)
    if not m:
        return html
    note("<main> landmark added")
    html = html[:m.end()] + '\n<main id="main-content" tabindex="-1">' + html[m.end():]
    f = html.rfind('<footer')
    if f == -1:
        f = html.rfind('</body>')
    return html[:f] + '</main>\n' + html[f:]


# ===========================================================================

def process(path):
    fname = os.path.basename(path)
    original = open(path, encoding='utf-8', errors='ignore').read()
    html = original
    tm = re.search(r'<title>(.*?)</title>', html, re.S)
    title = tm.group(1).strip() if tm else ''

    # Stage 1 — structure first, before anything is inserted.
    html = close_jsonld_script(html)
    html = close_head(html)
    html = ensure_lang(html)
    html = fix_malformed_attributes(html)
    html = fix_stray_closing_tags(html)
    html = fix_menu_nesting(html)
    html = fix_orphaned_tab_link(html)

    # Stage 2 — links.
    html = fix_orphan_paths(html, fname)
    html = fix_links(html)
    html = fix_extracurricular_targets(html)
    html = restore_tab_hrefs(html)
    html = fix_contact_nav(html)
    html = wire_dead_nav_item(html)
    html = drop_blank_target_on_internal(html)
    html = harden_external_links(html)
    html = comment_dead_stylesheet(html)

    # Stage 3 — metadata, performance, accessibility.
    html = font_display_swap(html)
    html = fix_jsonld(html)
    html = upgrade_head(html, fname, title)
    html = media_perf(html)
    html = label_blank_alt_thumbnails(html)
    html = add_skip_link(html)
    html = add_main_landmark(html)

    if html != original:
        open(path, 'w', encoding='utf-8').write(html)
        return True
    return False


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else '..'
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), target))
    changed = [f for f in sorted(glob.glob('*.html')) if process(f)]
    print("Modified %d files.\n" % len(changed))
    for k, v in sorted(LOG.items(), key=lambda kv: -kv[1]):
        print("  %5d  %s" % (v, k))
