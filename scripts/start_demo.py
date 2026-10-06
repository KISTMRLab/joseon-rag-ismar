"""Start this repository's bundled example; private data and model weights are optional.

By default the demo serves the bundled authored articles and works offline.
``--sample-crawl`` fetches a small Sejong Annals sample (one lunar month, at most
100 articles, about three minutes at 1.5 s per request; cached and resumable),
builds its index and serves it. ``--sample`` serves an already fetched sample
without touching the network. Neither runs unless asked.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CORPUS = 'data/sejong-sample.jsonl'
SAMPLE_INDEX = 'outputs/sejong-sample.index.json'
SAMPLE_QUESTION = '세종 2년 5월 살곶이 다리 공사를 감독한 사람은 누구인가?'
parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--port', type=int, default=8080)
parser.add_argument('--sample', action='store_true', help=f'serve the local Sejong sample ({SAMPLE_CORPUS}) instead of the authored examples; no network')
parser.add_argument('--sample-crawl', action='store_true', help='fetch the Sejong sample first (joseon-agent crawl --sample; cached reruns make no request), then serve it')
parser.add_argument('--skip-beat', action='store_true', help='Skip preparation; use the existing local cache or authored fixture when absent')
parser.add_argument('--skip-paper-method', action='store_true', help='Do not run scripts/prepare_paper_method.py; serve the BEAT demo adapter')
args = parser.parse_args()
os.chdir(ROOT)
os.environ['PYTHONPATH'] = str(ROOT / 'src') + os.pathsep + os.environ.get('PYTHONPATH', '')
prepare = ROOT / 'scripts' / 'prepare_viewer.py'
if prepare.exists() and not all((ROOT / 'static' / 'vendor' / name).is_file() for name in ('three.module.js', 'GLTFLoader.js', 'BufferGeometryUtils.js')):
    subprocess.run([sys.executable, str(prepare)], check=True)
subprocess.run([sys.executable, '-m', 'joseon_rag.cli', 'build', 'examples/articles.jsonl', '--out', 'outputs/demo.index.json'], check=True)


def sample_index(crawl: bool) -> str | None:
    """Build the sample index; return None (authored examples) when no sample corpus is available."""
    if crawl:
        print('Fetching the Sejong sample (one lunar month, at most 100 articles, 1.5 s between requests) ...', flush=True)
        if subprocess.run([sys.executable, '-m', 'joseon_rag.cli', 'crawl', '--sample', '--out', SAMPLE_CORPUS]).returncode:
            print('The sample crawl stopped (see the message above); rerun to resume from the cache.', flush=True)
    corpus = ROOT / SAMPLE_CORPUS
    if not corpus.is_file() or not corpus.read_text(encoding='utf-8').strip():
        print(f'No local sample at {SAMPLE_CORPUS}; serving the bundled authored examples. '
              'Fetch it with: python scripts/start_demo.py --sample-crawl', flush=True)
        return None
    subprocess.run([sys.executable, '-m', 'joseon_rag.cli', 'build', SAMPLE_CORPUS, '--out', SAMPLE_INDEX], check=True)
    return SAMPLE_INDEX


index = (sample_index(args.sample_crawl) if args.sample or args.sample_crawl else None) or 'outputs/demo.index.json'
extra = ['--question', SAMPLE_QUESTION] if index == SAMPLE_INDEX else []
if index != SAMPLE_INDEX and (ROOT / SAMPLE_CORPUS).is_file():
    print('A local Sejong sample exists; serve it with: python scripts/start_demo.py --sample', flush=True)
# >>> paperreach beat preparation (managed by tools/integrate-beat-methods.py)
# BEAT preparation and the optional paper-method hook are non-fatal: on failure
# the server still starts with the existing local cache or the authored starter.
paper_args = None
if not args.skip_beat:
    prepared = subprocess.run([sys.executable, str(ROOT/'scripts/prepare_beat_demo.py')])
    if prepared.returncode:
        print('BEAT preparation failed (see the message above); continuing with the existing local cache '
              'or the bundled authored starter. Retry with: python scripts/prepare_beat_demo.py', flush=True)
paper_hook = ROOT/'scripts/prepare_paper_method.py'
if paper_hook.exists() and not args.skip_paper_method:
    hook = subprocess.run([sys.executable, str(paper_hook)], stdout=subprocess.PIPE, text=True)
    print(hook.stdout or '', end='', flush=True)
    lines = [line for line in (hook.stdout or '').splitlines() if line.strip()]
    try:
        paper_result = json.loads(lines[-1]) if hook.returncode == 0 and lines else None
    except ValueError:
        paper_result = None
    if isinstance(paper_result, dict) and paper_result.get('ready'):
        os.environ['PAPER_METHOD_RESULT'] = json.dumps(paper_result)
        if isinstance(paper_result.get('server_args'), list) and paper_result['server_args']:
            paper_args = [str(arg) for arg in paper_result['server_args']]
    else:
        print('Paper-method preparation did not complete; serving the BEAT demo adapter instead. '
              'Details: python scripts/prepare_paper_method.py', flush=True)
# <<< paperreach beat preparation

print(f'Open http://127.0.0.1:{args.port}/ — ' + ('the local Sejong Annals sample is ready (data stays on this machine).' if extra else 'bundled starter samples are ready.'), flush=True)
raise SystemExit(subprocess.call([sys.executable, *(paper_args or ['-m', 'joseon_rag.cli', 'serve', index, '--events', 'examples/events.json', *extra]), '--port', str(args.port)]))
