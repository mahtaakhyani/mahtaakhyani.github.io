# Site update — CV 2026 alignment

Two scripts, run in this order against a fresh clone:

```
python3 fix_site.py        # structural + link + a11y repairs (all 16 pages)
python3 update_content.py  # CV content update (index.html + Mahta-Akhyani.html)
```

Both are idempotent. `update_content.py --dry-run` reports matches without writing.

`index.html` and `Mahta-Akhyani.html` are byte-identical duplicates, so every
content edit is applied to both.

---

## Content changes (find → replace)

### Hero bio — full rewrite
**Was:** "motivated researcher with a diverse science and engineering background…
eager to join a top research program as a dedicated team member…"

**Now:** three paragraphs — current position (M.Sc. GIST, Prof. Pilwon Hur, physical
HRI), current work (state anxiety estimation for adaptive exoskeleton control; trust
in physically coupled HRI), then prior work (modular ROS social-robot framework,
empathy-toward-robots in autism, SLAM pipe-inspection robot), closing on the
cross-disciplinary background as a capability rather than an apology.

The old text read as an undergraduate seeking a place. Nothing in it said what you
actually work on.

### Contact block
| Field | Was | Now |
|---|---|---|
| Email | `mahta.akhyani@gmail.com` | `mahta.akhyani@gm.gist.ac.kr` |
| Affiliation | `Affilliation: University of Tehran` | `Affiliation: Gwangju Institute of Science and Technology (GIST), South Korea` |

### Research interests — now matches the CV's four
- `Bio-inspired robotics` → `Biomechanics`
- `Cognitive robotics` → `Wearable robots and exoskeletons`
- `Wearable sensors` → `Social cognitive robots`
- `Human-Robot Interaction (HRI)` — unchanged

Intro paragraph rewritten from "intersection of robotics, artificial intelligence, and
biological engineering… fascinated by technologies that integrate insights from nature"
to a direct statement about physically coupled human-machine systems.

### About carousel 1/4
**Was:** "I'm a skilled engineer in programming with python, self-learned ROS, and have
done projects with it. I've also passed a Django course with a full 100 marks, from
UTech academy and was employed by them as a top-five student after that."

**Now:** "I'm an M.Sc. student in Mechanical and Robotics Engineering at GIST, South
Korea, advised by Prof. Pilwon Hur. Before that I read Chemical Engineering
(biotechnology) at the University of Tehran, and worked across robotics, computer
vision and back-end engineering."

Thesis title corrected to the CV wording:
`"The role of SLAM robots in pipe inspection in chemical andpetroleum industries"`
→ `"Design of mobile robot with SLAM capabilities for pipe inspection in chemical and petroleum industries"`

### About carousel 2/4 — lab dates
Three posts were still marked "Present".

| Lab | Was | Now |
|---|---|---|
| TeraHertz Systems | July 2022 – Present | Aug 2022 – Oct 2023 |
| Advanced Robotics | Aug 2021 – Present | Jun 2021 – Jul 2024 |
| Chem-E-Car | March 2019 – March 2020 | Mar 2019 – Feb 2020 |

`Dr.` → `Prof.` for Neshat, Moradi and Zarghami, matching the CV.

### About carousel 3/4 — hard skills
Added from the CV's Proficient/Experienced tiers: Gazebo simulation, Git, Computer
vision (OpenCV, MediaPipe), Raspberry Pi / Arduino / Jetson Nano, C/C++ / TensorFlow /
NumPy / Pandas.

### About carousel 4/4 and typos
- `Invasive Brain Stimulation` → `Non-Invasive Brain Stimulation`. This one was a
  factual inversion — the head-phantom work is *for* non-invasive stimulation, so the
  site was advertising the opposite of the research.
- `Biomechanics and Eexoskeleton` → `Biomechanics and Exoskeletons`
- `Creativite thinking` → `Creative thinking`
- `Affilliation` → `Affiliation`

### Head metadata
`description`, `keywords`, `og:description` and `twitter:description` all still said
"Student at faculty of applied sciences, University of Tehran" and "masters position
seeking". Rewritten around GIST, pHRI, biomechanics, wearable robots and social
cognitive robots.

---

## Structural repairs (from `fix_site.py`)

The critical one: `chem-e-car.html`, `electrical-compass.html`,
`firefighting-robot.html` and `line-following-robot.html` each opened
`<script type="application/ld+json">` and never closed it. The browser swallowed the
rest of the document as script text — up to 41,599 characters — so those four pages
rendered **completely blank**. Now closed.

Also: ~200 broken internal links repaired (`Phantom.html`, `Compass.html`, `FFR.html`,
`LFR.html`, `WWT.html`, three pages whose every path started `../`); 9 missing
`</head>`; canonical URLs that contained a page title instead of a URL; JSON-LD
describing you as an `Organization` named `WebSite95300`, now a `Person`; 151
`target="_blank"` links given `rel="noopener noreferrer"`; the Extracurricular submenu,
which pointed every item at an unrelated robotics page; 420 images lazy-loaded and 50
videos given `preload="none"`.

All 16 pages now parse with 0–4 errors (was 7–18). The remainder are pre-existing
unclosed `<div>`s in Nicepage output that browsers recover from; fixing them blind
would risk changing layout.

---

## Not done — needs your input

1. **No publications section exists.** This is the biggest remaining gap. The CV lists
   an ICROS 2026 paper, the ACM THRI submission under major revision, two arXiv
   preprints and one in preparation. None of it appears anywhere on the site. This
   should probably be its own section on the homepage, above Projects. I did not build
   it because it needs new Nicepage section markup and a decision about where it sits.

2. **"I've defended my B.Sc. thesis … with a full mark in May 2022."** I changed this
   to "with the highest grade" and dropped the date. Your CV gives the thesis project
   as 04/2022–07/2022 and the B.Sc. as 2018–2023, so "May 2022" may be wrong — but I
   couldn't confirm the real defence date from the CV, so I removed rather than
   guessed. Tell me the date and I'll put it back.

3. **Selected Projects section** still describes only the B.Sc.-era work (SLAM thesis,
   Chem-E-Car, Fanjoo). It doesn't mention the GIST Trust-POMDP work, the anxiety
   estimation paper, or the head phantom. Worth extending.

4. **Missing skills/languages.** The CV lists Persian / English (IELTS 8.0) / Korean
   and the IELTS certification. The site has no languages block at all.

5. **Old teaching + professional experience** (Advanced Robotics TA, RoboTech Academy,
   Azta Club junior full-stack, UTech, Fanjoo) — only Fanjoo and UTech appear, and
   Azta Club (01/2025–06/2025) is absent entirely.

6. **Repository weight.** 456 MB of git history against 264 MB of images and 169 MB of
   files, including a 37 MB MP4 and a 35 MB GIF. Compression is the single biggest
   remaining performance win and it isn't a markup problem.

7. **Still missing assets:** `images/dotIR.jpg`, `images/line-following.jpg`,
   `images/bulb_yellow.mp4` (it's in your `.gitignore`), `files/Vid-20200129-Wa0007.mp4`,
   and `Post-Template.css` (referenced by four pages, never in the repo — I commented
   the references out with a restore note rather than deleting them).
