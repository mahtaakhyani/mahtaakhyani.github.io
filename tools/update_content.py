#!/usr/bin/env python3
"""
update_content.py — brings the site copy in line with Mahta_Akhyani_CV2026.pdf.

Every replacement below is a literal find/replace pair. Facts come only from
the CV; nothing is invented. index.html and Mahta-Akhyani.html are byte-identical
duplicates, so both receive the same edits.
"""
import glob
import os
import sys

PAIRS = []


def sub(old, new, label):
    PAIRS.append((old, new, label))


# ---------------------------------------------------------------------------
# 1. HERO BIO — was written as a chemical-engineering undergraduate looking for
#    a research programme. She is now an M.Sc. researcher at GIST with a
#    publication record.
# ---------------------------------------------------------------------------
sub(
    'I am a motivated researcher with a diverse science and engineering background '
    'spanning chemical engineering, computer science, and robotics. My honors thesis '
    'designing mobile robots demonstrates my ability to bridge theory and hands-on '
    'engineering. Through teaching, volunteering, and extracurricular projects, I have '
    'honed my communication, collaboration, and problem-solving skills.&nbsp;<br>\n'
    '                        <br>My goal is to leverage technologies like AI and soft '
    'robotics to make impactful discoveries and innovations.&nbsp;<br>I am eager to join '
    'a top research program as a dedicated team member, drawing on my adaptability and '
    'relentless work ethic to advance cutting-edge projects.&nbsp;<br>',

    'I am an M.Sc. researcher in Mechanical and Robotics Engineering at the Gwangju '
    'Institute of Science and Technology (GIST), working with Prof. Pilwon Hur. My '
    'research is on physical human-robot interaction: how a person\'s internal state '
    'shapes their experience of being coupled to a machine, and how a robot should '
    'respond to it.&nbsp;<br>\n'
    '                        <br>Right now I work on real-time state anxiety estimation '
    'for adaptive wearable exoskeleton control, and on trust in physically coupled '
    'human-robot interaction. Earlier I built a modular ROS framework for rapid social '
    'robot development, studied empathy toward robots in autism, and designed a '
    'SLAM-capable mobile robot for pipe inspection in the petrochemical industry.&nbsp;<br>\n'
    '                        <br>An engineering background spanning chemical '
    'engineering, computer science and robotics lets me move between materials, '
    'algorithms and the human side of a system in the same project.&nbsp;<br>',
    "hero bio rewritten around current GIST research"
)

# ---------------------------------------------------------------------------
# 2. CONTACT / AFFILIATION — old address and institution; "Affilliation" typo.
# ---------------------------------------------------------------------------
sub(
    '<span style="font-style: italic;">Email</span>: mahta.akhyani@gmail.com',
    '<span style="font-style: italic;">Email</span>: mahta.akhyani@gm.gist.ac.kr',
    "email updated to GIST address"
)
sub(
    '<span style="font-style: italic;">Affilliation</span>: University of Tehran',
    '<span style="font-style: italic;">Affiliation</span>: Gwangju Institute of '
    'Science and Technology (GIST), South Korea',
    "affiliation updated to GIST (and spelling fixed)"
)

# ---------------------------------------------------------------------------
# 3. RESEARCH INTERESTS — align with the CV's four stated interests.
# ---------------------------------------------------------------------------
sub(
    'My research interests sit at the intersection of robotics, artificial '
    'intelligence, and biological engineering. I am fascinated by technologies that '
    'integrate insights from nature with advanced engineering to create innovative '
    'solutions. Specifically, I am interested in topics such as:',

    'My research sits where robotics meets human physiology and cognition — '
    'specifically, how people and machines behave when they are physically coupled to '
    'each other. I work on:',
    "research-interests intro rewritten"
)
sub(
    '<span style="font-weight: 700;">Bio-inspired robotics</span>',
    '<span style="font-weight: 700;">Biomechanics</span>',
    "interest: Bio-inspired robotics -> Biomechanics"
)
sub(
    '<span style="font-weight: 700;">Cognitive robotics</span>',
    '<span style="font-weight: 700;">Wearable robots and exoskeletons</span>',
    "interest: Cognitive robotics -> Wearable robots"
)
sub(
    '<span style="font-weight: 700;">Wearable sensors</span>',
    '<span style="font-weight: 700;">Social cognitive robots</span>',
    "interest: Wearable sensors -> Social cognitive robots"
)

# ---------------------------------------------------------------------------
# 4. ABOUT CAROUSEL 1/4 — undergraduate framing, and a misquoted thesis title.
# ---------------------------------------------------------------------------
sub(
    '<span style="font-weight: 700;">I</span>\'m a skilled engineer in programming with '
    'python, self-learned ROS, and have done projects with<span style="font-style: '
    'italic;"></span>\n'
    '                          <span style="font-style: italic;">it. I\'ve also passed a '
    'Django course with a full 100 marks, from UTech academy and was employed by them as '
    'a top-five student after that.',

    '<span style="font-weight: 700;">I</span>\'m an M.Sc. student in Mechanical and '
    'Robotics Engineering at GIST, South Korea, advised by Prof. Pilwon Hur. Before '
    'that I read Chemical Engineering (biotechnology) at the University of Tehran, and '
    'worked across robotics, computer vision and back-end engineering.<span '
    'style="font-style: italic;"></span>\n'
    '                          <span style="font-style: italic;">',
    "About 1/4 rewritten for current standing"
)
sub(
    '"The role of SLAM robots in pipe inspection in chemical andpetroleum industries"'
    '</span>, with a full mark in May 2022.',
    '"Design of mobile robot with SLAM capabilities for pipe inspection in chemical and '
    'petroleum industries"</span>, with the highest grade.',
    "B.Sc. thesis title corrected to match the CV"
)

# ---------------------------------------------------------------------------
# 5. ABOUT CAROUSEL 2/4 — lab dates said "Present" for posts that have ended.
# ---------------------------------------------------------------------------
sub('<br>Supervisor: Dr. M. Neshat<br>July 2022 - Present<br>',
    '<br>Supervisor: Prof. Mohammad Neshat<br>Aug 2022 - Oct 2023<br>',
    "Terahertz lab dates closed (Aug 2022 - Oct 2023)")
sub('<br>Advisor: Dr. Hadi Moradi<br>Aug 2021 - Present<br>',
    '<br>Advisor: Prof. Hadi Moradi<br>Jun 2021 - Jul 2024<br>',
    "Advanced Robotics lab dates closed (Jun 2021 - Jul 2024)")
sub('<br>Advisor: Dr. Reza Zarghami<br>March 2019 - March 2020<br>',
    '<br>Advisor: Prof. Reza Zarghami<br>Mar 2019 - Feb 2020<br>',
    "Chem-E-Car dates corrected (Mar 2019 - Feb 2020)")

# ---------------------------------------------------------------------------
# 6. ABOUT CAROUSEL 4/4 — the head-phantom work targets NON-invasive brain
#    stimulation; the site said the opposite. Also two spelling errors.
# ---------------------------------------------------------------------------
sub('Biomechanics and Eexoskeleton', 'Biomechanics and Exoskeletons',
    "typo: Eexoskeleton -> Exoskeletons")
sub('Invasive Brain Stimulation to control mental or physical disorders',
    'Non-Invasive Brain Stimulation to control mental or physical disorders',
    "corrected to NON-invasive brain stimulation")
sub('Creativite thinking', 'Creative thinking', "typo: Creativite -> Creative")

# ---------------------------------------------------------------------------
# 7. HARD SKILLS — extend the list to the CV's "Proficient" tier.
#    Appended as new <li> items in the existing markup pattern.
# ---------------------------------------------------------------------------
ICON = ('<div class="u-list-icon">\n'
        '                                      <div xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xml:space="preserve" '
        'class="u-svg-content" style="font-size: 1.1em; margin: -1.1em;">\u2714</div>\n'
        '                                    </div>')

def li(text):
    return ('<li>\n                                    ' + ICON + text +
            '\n                                  </li>\n                                  ')

sub('<li>\n                                    ' + ICON + 'Django REST\n'
    '                                  </li>\n'
    '                                </ul>',

    '<li>\n                                    ' + ICON + 'Django REST\n'
    '                                  </li>\n                                  '
    + li('Gazebo simulation')
    + li('Git')
    + li('Computer vision (OpenCV, MediaPipe)')
    + li('Raspberry Pi, Arduino, Jetson Nano')
    + li('C/C++, TensorFlow, NumPy, Pandas').rstrip() + '\n'
    '                                </ul>',
    "hard skills extended from the CV"
)


def apply(path, dry):
    src = open(path, encoding='utf-8', errors='ignore').read()
    orig = src
    hits, misses = [], []
    for old, new, label in PAIRS:
        n = src.count(old)
        if n == 0:
            if new not in src:
                misses.append(label)
            continue
        src = src.replace(old, new)
        hits.append((label, n))
    if not dry and src != orig:
        open(path, 'w', encoding='utf-8').write(src)
    return hits, misses


if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    for f in ['index.html', 'Mahta-Akhyani.html']:
        hits, misses = apply(f, dry)
        print("== %s ==" % f)
        for label, n in hits:
            print("   applied x%d  %s" % (n, label))
        for label in misses:
            print("   NOT FOUND   %s" % label)
        print()
