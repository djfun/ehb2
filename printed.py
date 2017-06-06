import imghdr
import os
from collections import defaultdict
from urllib.parse import quote

import re
import requests
from helpers import logger
from flask import send_file
from flask_login import login_required
from __init__ import *

from helpers import *
from flask import request, flash
from config import conf, end_date, start_date, number_of_days, read_songs

import tempfile
import shutil

parts = ["", "Tenor", "Lead", "Bari", "Bass"]

def latex_has_errors(texlog):
    with open(texlog, "r") as f:
        for line in f:
            if line.startswith("!"):
                return True
    return False

def compile_and_send_pdf(pdf_filename, contents, runs=1, dirpath=None):
    if not dirpath:
        dirpath = tempfile.mkdtemp()

    texfile = os.path.join(dirpath, "file.tex")
    pdffile = os.path.join(dirpath, "file.pdf")
    logfile = os.path.join(dirpath, "file.texlog")

    logger().info("Temp directory for %s is %s" % (pdf_filename, dirpath))

    with open(texfile, "w", encoding="utf-8") as f:
        f.write(contents)

    old_cwd = os.getcwd()
    os.chdir(dirpath)

    for i in range(runs):
        os.system("pdflatex -interaction=nonstopmode file.tex > file.texlog")

    os.chdir(old_cwd)

    if os.path.exists(pdffile) and not latex_has_errors(logfile):
        return send_file(pdffile, mimetype='application/pdf')
    else:
        texlog = open(os.path.join(dirpath, "file.texlog"), encoding="iso-8859-1").read()
        errstr = "An error occurred when compiling the LaTeX file for %s.\n\nLaTeX output was:\n%s" % (pdf_filename, texlog)
        return errstr.replace("\n", "<br/>\n")


@app.route("/dancecard.pdf")
@login_required
def generate_dancecard():
    participants = []
    labels = defaultdict(list)

    column = 0
    previous_part = None

    stickers_per_row = 4

    for p in session.query(Participant).order_by(Participant.final_part).order_by(Participant.lastname):
        name = "%s %s" % (p.firstname, p.lastname)
        part = parts[p.final_part]
        column += 1

        if part != previous_part:
            column = 0
            previous_part = part
        elif column >= stickers_per_row:
            column = 0
            labels[part].append("")

        labels[part].append(name)

    tex = render_template("printed/dancecard.tex", shortname=conf.get("application", "shortname"),
                           tenors=labels["Tenor"], leads=labels["Lead"], baris=labels["Bari"], basses=labels["Bass"])

    return compile_and_send_pdf("dancecard.pdf", tex)


@app.route("/envelope-stickers.pdf")
@login_required
def generate_envelope_stickers():
    current_page = []
    pages = [current_page]
    x = 1
    y = 1
    labels_per_row = 3
    rows_per_page = 8

    for p in session.query(Participant).order_by(Participant.lastname):
        if x > labels_per_row:
            x = 1
            y += 1

            if y > rows_per_page:
                y = 1
                current_page = []
                pages.append(current_page)

        current_page.append((x, y, p.lastname, p.firstname))
        x += 1

    tex = render_template("printed/env-stickers.tex", pages=pages)
    return compile_and_send_pdf("envelope-stickers.pdf", tex, runs=2)

@app.route("/dancecard-stickers.pdf")
@login_required
def generate_dancecard_stickers():
    participants = []

    for p in session.query(Participant).order_by(Participant.final_part).order_by(Participant.lastname):
        email = p.email.replace("_", "\\_")

        participants.append({"name": "%s %s" % (p.firstname, p.lastname),
                             "city": "%s / %s" % (p.city, p.country),
                             "email": email,
                             "part": parts[p.final_part]
                             })

    tex = render_template("printed/dancecard-stickers.tex", participants=participants)
    return compile_and_send_pdf("dancecard-stickers.pdf", tex, runs=2)






######################### MAKING BADGES ################################


def download_binary_file(url, filename):
    url = url
    response = requests.get(url, stream=True)
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


def download_qr(iq_username, filename):
    if not iq_username:
        return None

    elif os.path.exists(filename):
        return filename

    else:
        download_binary_file("http://www.instantquartet.org/qre/%s" % quote(iq_username), filename)

        if imghdr.what(filename) == "png":
            return filename
        else:
            # not a valid PNG file
            return None


def e(x):
    return x.encode('utf-8')


def makebadge(i, p:Participant, dir):
    filename = os.path.join(dir, "%d.png" % p.id)
    qr = download_qr(p.iq_username, filename)
    if qr == None:
        qr = ""

    pos = "topbadge_bottom_left" if i%2 == 0 else "current page.south west"

    return "  \\badge{%s}{%s}{%s}{%s}{%s}{%s}{%s}{%s}" % \
           (pos, p.firstname, p.lastname, p.city, p.country, parts[p.final_part], p.country, qr)


class MutableBoolean:
    val = False


def print_end(f, just_ended:MutableBoolean):
    if not just_ended.val:
        f.write( end + "\n")
        just_ended.val = True

def close(f, i, just_ended:MutableBoolean):
    if f != None:
        if i % 2 != 0:
            print_end(f, just_ended)
        f.close()



start = r"""
\newpage

\begin{tikzpicture}[remember picture, overlay]
  \fill [fill=PPPPP] ($(current page.south west) + (0.5\paperwidth-40,0)$) rectangle (current page.north east);

  \coordinate (qp) at (0.25\paperwidth, 0.25\paperheight);
  \coordinate (hpx) at (0.5\paperwidth, 0);
  \coordinate (hpy) at (0, 0.5\paperheight);
  \coordinate (topbadge_bottom_left) at ($(current page.west) + (0,-0.4)$);

% separator lines
  \draw (current page.south) -- (current page.north);
 % \draw (current page.west) -- (current page.east);
%

"""

end = r"""
\end{tikzpicture}
"""


@app.route("/badges.pdf")
@login_required
def generate_badges():
    dirpath = tempfile.mkdtemp()
    logger().info("Temp directory for badges is %s" % (dirpath))

    # ensure paths exist
    iqdir = os.path.join(dirpath, "iq")
    if not os.path.exists(iqdir):
        os.makedirs(iqdir)

    flagdir = os.path.join(dirpath, "flags")
    if not os.path.exists(flagdir):
        os.makedirs(flagdir)

    shutil.copyfile("static/Logo.pdf", os.path.join(dirpath, "Logo.pdf"))

    songs = read_songs()

    i = 0
    prev_part = -1
    just_ended = MutableBoolean() # type: MutableBoolean
    just_ended.val = False
    f = None

    for p in session.query(Participant).order_by(Participant.final_part):
        # download flag if necessary
        flag_filename = os.path.join(flagdir, "%s.png" % p.country)
        if not os.path.exists(flag_filename):
            download_binary_file("http://flagpedia.net/data/flags/normal/%s.png" % p.country.lower(), flag_filename)

        fp = p.final_part

        if fp != prev_part:
            if f:
                f.flush()
                close(f, i, just_ended)

            local_tex_name = "%s.tex" % parts[fp]
            f = open(os.path.join(dirpath, local_tex_name), "w", encoding="utf-8")
            prev_part = fp
            i = 0

        if i % 2 == 0:
            f.write(start.replace("PPPPP", parts[prev_part]) + "\n")
            just_ended.val = False

        f.write(makebadge(i, p, iqdir) + "\n")

        just_ended.val = False
        i = i + 1

        if i % 2 == 0:
            print_end(f, just_ended)

    f.flush()
    close(f, i, just_ended)

    template = texenv.get_template('printed/badges.tex')
    tex = template.render(event_name=conf.get("application", "name"), songs=songs)

    # tex = render_template("printed/badges.tex", event_name=conf.get("application", "name"), songs=songs)
    return compile_and_send_pdf("badges.pdf", tex, runs=2, dirpath=dirpath)

