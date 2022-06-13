#!/usr/bin/python3
# Author: Tim Schupp
from collections import namedtuple
import logging as log
import os
import argparse
import subprocess

desc = """ 
A cli interface for some inkscape funtionality.

It can:
- export square area by tag
- list all tags
- export all tags with specific prefix
and more...
"""

# If used dont want to set ENV, use this:
INKSCAPE_EXE = os.environ.get("INKSCAPE_EXE", None)


def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--prefix', default="EXPORT_")
    parser.add_argument('-i', '--input', default=None)
    parser.add_argument('-o', '--output', default=None)
    parser.add_argument('-t', '--tag', default=None)

    parser.add_argument('-a', '--all', action="store_true")
    parser.add_argument('-l', '--list', action="store_true")
    parser.add_argument('-x', '--export', action="store_true")

    parser.add_argument('-exe', '--inkscape-executable', default=os.environ.get("INKSCAPE_EXE", INKSCAPE_EXE))

    parser.add_argument('-v', '--verbose', action="store_true")

    return parser.parse_args()

def get_all_inkscape_tags(args : argparse.Namespace) -> list:
    """ get all tags of an inkscape file """
    fetches = f"{args.inkscape_executable} {args.input} --query-all"
    out = os.popen(fetches).read().split("\n")[:-1]
    return [ l.split(",")[0] for l in out ]

def get_all_inkscape_tags_filtered(args) -> list:
    """ only the tags that start with 'prefix' """
    return [ x for x in get_all_inkscape_tags(args) if x.startswith(args.prefix) ]

def maybe_append_slash_dir(dir : str) -> str:
    """ incase dir had no slash """
    if not dir.endswith("/"):
        dir += "/"
    return dir

def export_by_tag(tag : str, out_name : str, out_dir: str) -> None:
    """ general function to export a specific tag and prefix """
    log.debug(f'Exporting "{tag}" as "{out_name}.pdf"')
    cmd = f'{args.inkscape_executable} {args.input} --with-gui --batch-process --actions="select-by-id:{tag};FitCanvasToSelection;EditDelete;export-filename:{out_dir}{out_name}.pdf;export-area-page;export-do"'
    log.debug(f'Running inkscape in visual mode: "{cmd}"')
    out = subprocess.run(cmd, shell=True)
    assert not out.returncode, f"Failed tag extraction: {tag}\non command: {cmd}"

def run_export_action(args) -> None:
    """ exports a single arg starting with 'prefix' and then 'tag' """
    assert args.tag, "Needed tag name to export"
    assert args.output, "please provide output directory"

    log.debug(f'Opening inkscape to export by name {args.tag}')
    tag = args.tag

    if args.prefix:
        log.debug(f'Found prefix {args.prefix}, using it, looking for {args.prefix}{args.tag}')
        tag = args.prefix + args.tag

    out_dir = maybe_append_slash_dir(args.output)
    export_by_tag(tag, args.tag, out_dir)

def run_list_action(args : argparse.Namespace):
    """ list all elements that start with 'prefix' """
    log.debug(f'Opening inkscape to find all tags with "{args.prefix}"')
    all_filtered_tags = get_all_inkscape_tags_filtered(args)
    log.info(f'Tags found: {all_filtered_tags}')

def run_all_action(args : argparse.Namespace):
    """ exports all elements that start with 'prefix' """
    assert args.output, "please provide output directory"

    out_dir = maybe_append_slash_dir(args.output)

    log.debug(f'Opening inkscape to export all squares with "{args.prefix}"')
    all_filtered_tags = get_all_inkscape_tags_filtered(args)
    log.info(f'Tags found: {all_filtered_tags}')

    for tag in all_filtered_tags:
        out_name = tag[len(args.prefix):]
        export_by_tag(tag, out_name, out_dir)

if __name__ == "__main__":
    args = parse_args()

    log.basicConfig(level=log.DEBUG if args.verbose else log.INFO)

    actions = [
        args.export,
        args.list,
        args.all
    ]

    action_funcs = [
        run_export_action,
        run_list_action,
        run_all_action
    ]

    assert INKSCAPE_EXE, "Please provice inkscape executable, either via env.INKSCAPE_EXE, or -exe"
    assert sum(actions) == 1, f"only one action can be used -a,-l,-x {actions}"
    assert sum(actions) != 0, f"plese specify at least one action -a,-l,-x"

    assert args.input, "need svg input file"

    action_funcs[actions.index(True)](args)



