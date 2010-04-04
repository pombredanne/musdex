# VCS routines for musdex
#
# Copyright 2010 Max Battcher. Some rights reserved.
# Licensed for use under the Ms-RL. See attached LICENSE file.
from config import BASEDIR, load_index, save_index, save_config
from handlers import get_handler
import logging
import os.path

import vcs

def add(args, config):
    index = load_index(config)

    for archive in args.archive:
        archive = os.path.relpath(archive)
        if 'archives' in config \
        and any(arc['filename'] == archive for arc in config['archives']):
            logging.warn("Archive already configured: %s" % archive)
            continue

        handler = get_handler(args.handler)
        arch = handler(archive, os.path.join(BASEDIR, archive))
        if not arch.check():
            logging.error("Archive not supported by given handler: %s: %s" % (
                args.handler, archive))

        logging.info("Extracting archive for the first time: %s" % archive)
        files = handler.extract(force=True)
        for f, t in files:
            index[f] = t
            vcs.add_file(config, f)

        entry = {'filename': archive}
        if args.handler: entry['handler'] = args.handler
        if 'archives' not in config: config['archives'] = []
        config['archives'].append(entry)

    save_config(args, config)
    save_index(config, index)

def extract(args, config):
    index = load_index(config)
    index_updated = False

    if args.archive: args.archive = map(os.path.relpath, args.archive)

    manifest = vcs.manifest(config)

    for archive in config['archives']:
        arcf = archive['filename']
        arcloc = os.path.join(BASEDIR, arcf)
        if args.archive and arcf not in args.archive:
            continue

        arcman = dict((f, index[f] if f in index else None) \
            for f in manifest if f.startswith(arcloc))

        hname = archive['handler'] if 'handler' in archive else None
        handler = get_handler(hname)
        arch = handler(arcf, arcloc, manifest=arcman)
        files = arch.extract(force=args.force or arcloc not in index)
        if files: index_updated = True

        for f, t in files:
            index[f] = t
            if f not in arcman: vcs.add_file(config, f)
            
    if index_updated: save_index(config, index)

def combine(args, config):
    index = load_index(config)
    index_updated = False

    if args.archive: args.archive = map(os.path.relpath, args.archive)

    manifest = vcs.manifest(config)

    for archive in config['archives']:
        arcf = archive['filename']
        arcloc = os.path.join(BASEDIR, arcf)
        if args.archive and arcf not in args.archive:
            continue

        arcman = dict((f, index[f] if f in index else None) \
            for f in manifest if f.startswith(arcloc))

        hname = archive['handler'] if 'handler' in archive else None
        handler = get_handler(hname)
        arch = handler(arcf, arcloc, manifest=arcman)
        files = arch.combine(force=args.force or arcloc not in index)
        if files: index_updated = True

        for f, t in files:
            index[f] = t

        # TODO: Check for deleted files?

    if index_updated: save_index(config, index)

# vim: ai et ts=4 sts=4 sw=4
