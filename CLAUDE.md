# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state

This repository is **a bare scaffold** — there is no source code, build system, dependency manifest, or tests yet. The only committed file is `README.md` (placeholder). Everything below describes the empty directory layout that has been created in anticipation of development.

When implementing the project, update this file with the real build/lint/test commands and architecture once they exist.

## Directory layout

The directory names suggest a media/audio processing pipeline (the repo name `yusuke-trap` and `lirycs` point at music/trap-genre content):

- `input/audio/` — source audio files to be processed
- `input/image/` — source image files
- `lirycs/` — lyrics (note: directory name is misspelled; "lyrics")
- `output/` — generated/processed artifacts
- `run-books/` — operational runbooks / procedures
- `src/` — source code (currently empty)

All of these directories except `src` and `README.md` are currently empty and **untracked by git** (empty dirs are not committed). Decide on a `.gitkeep` convention or `.gitignore` rules when the structure firms up.

## Notes

- No language/toolchain has been chosen yet — there is no `package.json`, `requirements.txt`, `Cargo.toml`, etc. Confirm the intended stack before scaffolding build tooling.
