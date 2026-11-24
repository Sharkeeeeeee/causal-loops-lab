"""SPDX-License-Identifier: MIT. Step 3: publish the guesses and salt (only after the answers are sent).

Usage (from the repository root):  python -B ctc/blockchain/reveal.py
"""
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent


def main():
    if not (HERE / 'public' / 'loop_messages.json').exists():
        sys.exit('send the answers first (send.py)')
    target = HERE / 'public' / 'reveal.json'
    if target.exists():
        sys.exit('already revealed')
    shutil.copyfile(HERE / 'private' / 'reveal.json', target)
    print(f'revealed: {target}; now run verify.py')


if __name__ == '__main__':
    main()
