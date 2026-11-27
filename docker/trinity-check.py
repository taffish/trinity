"""Offline packaging checks; no replacement of upstream scientific code."""
import hashlib
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile

ROOT = Path('/opt/trinity')
VERSION = 'Trinity version: Trinity-v2.16.5'
VERSION_WARNING = "-ERROR: couldn't run the network check to confirm latest Trinity software version."
TOOLS = 'Trinity TrinityStats.pl align_and_estimate_abundance.pl abundance_estimates_to_matrix.pl insilico_read_normalization.pl ParaFly seqtk-trinity inchworm Chrysalis QuantifyGraph GraphFromFasta ReadsToTranscripts bamsifter slclust collectl bowtie2 bowtie2-build jellyfish samtools salmon blastn makeblastdb java perl python3 bash gzip bzip2 xz'.split()
BINARIES = ['Inchworm/bin/inchworm', 'Chrysalis/bin/Chrysalis',
            'Chrysalis/bin/QuantifyGraph', 'Chrysalis/bin/GraphFromFasta',
            'Chrysalis/bin/ReadsToTranscripts', 'trinity-plugins/BIN/ParaFly',
            'trinity-plugins/BIN/seqtk-trinity', 'trinity-plugins/bamsifter/_sift_bam_max_cov',
            'trinity-plugins/slclust/bin/slclust']


def run(args, expected=0):
    # Debian/Ubuntu compiler metadata can contain non-UTF8 bytes; preserve them
    # as explicit byte escapes rather than failing a valid version command.
    result = subprocess.run([str(x) for x in args], text=True, errors='backslashreplace', stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=840)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    if result.returncode != expected:
        raise RuntimeError(f'command={args!r} exit={result.returncode}, expected={expected}')
    return result


def version_ok(result):
    # Upstream redirects STDERR to STDOUT before printing its optional warning.
    # Accept only the exact version and this known offline diagnostic, not any
    # arbitrary banner containing a version substring or a nonzero command.
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return result.returncode == 0 and lines in ([VERSION], [VERSION, VERSION_WARNING])


def identity():
    assert not shutil.which('curl'), 'Unexpected curl enables upstream network version checks'
    assert version_ok(run(['Trinity', '--version'])), 'Incorrect runtime identity'
    for relative, checksum in {
        'Trinity': '7b21ffe45a692e4f27d0138027d3975af4ee909bd6a522f3fb4f5baddd16839d',
        'Butterfly/Butterfly.jar': '4293c8bcb6d861d9b8409c410d3aa9de77de567119d8743a555038528ece73bb',
        'util/support_scripts/salmon_runner.pl': 'ab6c386e4aa9453d9063ce0f46f7a6a5c9676623ec9dab107793d4741b75c92b',
    }.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == checksum
    assert run(['salmon', '--version']).stdout.strip() == 'salmon 2.12.0'
    salmon_linkage = run(['ldd', '/opt/salmon/salmon'])
    assert 'not found' not in salmon_linkage.stdout + salmon_linkage.stderr
    assert run(['samtools', '--version']).stdout.splitlines()[0] == 'samtools 1.19.2'
    assert run(['jellyfish', '--version']).stdout.strip() == 'jellyfish 2.3.1'
    assert 'version 2.5.2' in run(['bowtie2', '--version']).stdout
    run(['java', '-version'])
    assert run(['java', '-jar', ROOT/'trinity-plugins/Trimmomatic/trimmomatic.jar', '-version']).stdout.strip() == '0.40'
    run(['perl', '-MDB_File', '-MURI::Escape', '-e1'])
    run(['python3', '-c', 'import numpy'])
    for tool in TOOLS:
        path = Path(shutil.which(tool) or '/missing-command')
        assert path.is_file() and os.access(path, os.X_OK), tool
    for relative in BINARIES:
        path = ROOT / relative
        assert path.is_file() and os.access(path, os.X_OK), relative
        result = run(['ldd', path])
        assert 'not found' not in result.stdout + result.stderr, relative
    print('TRINITY_IDENTITY_PASS')


def help_check():
    # Upstream prints help via Perl die(), hence its documented exit 255.
    for option, markers in [('--help', ['Trinity --seqType', '--max_memory']),
                            ('--show_full_usage_info', ['--no_normalize_reads', '--genome_guided_bam'])]:
        result = run(['Trinity', option], 255)
        assert all(s in result.stdout + result.stderr for s in markers)
    result = run(['Trinity', '--taffish-invalid-option'], 255)
    assert "don't recognize parameter" in result.stdout + result.stderr
    print('TRINITY_HELP_PASS')


def fixtures():
    rng = random.Random(2161)
    transcripts = [''.join(rng.choice('ACGT') for _ in range(1200)) for _ in range(3)]
    Path('transcripts.fa').write_text(''.join(f'>tx{i}\n{s}\n' for i, s in enumerate(transcripts)))
    left, right = [], []
    complement = str.maketrans('ACGT', 'TGCA')
    for i, sequence in enumerate(transcripts):
        for offset in range(0, 951, 5):
            for replicate in range(3):
                name = f'read{i}_{offset}_{replicate}'
                r1 = sequence[offset:offset+100]
                r2 = sequence[offset+150:offset+250].translate(complement)[::-1]
                left.append(f'@{name}/1\n{r1}\n+\n' + 'I'*100 + '\n')
                right.append(f'@{name}/2\n{r2}\n+\n' + 'I'*100 + '\n')
    Path('left.fq').write_text(''.join(left))
    Path('right.fq').write_text(''.join(right))
    print('TRINITY_FIXTURE_PASS')


def stats():
    Path('tiny.fa').write_text('>TRINITY_DN0_c0_g1_i1\n'+'ACGT'*7+'\n>TRINITY_DN0_c0_g2_i1\n'+'ACGT'*3+'\n')
    text = run(['TrinityStats.pl', 'tiny.fa']).stdout
    assert 'Total trinity transcripts: 2' in ' '.join(text.split())
    assert 'Contig N50: 28' in text
    print('TRINITY_STATS_PASS')


def normalize():
    fixtures()
    run(['insilico_read_normalization.pl', '--seqType', 'fq', '--JM', '1G',
         '--max_cov', '50', '--left', 'left.fq', '--right', 'right.fq',
         '--pairs_together', '--CPU', '1', '--output', 'norm'])
    for name in ['left.norm.fq', 'right.norm.fq']:
        data = Path('norm', name).read_text().splitlines()
        assert data and len(data) % 4 == 0
    print('TRINITY_NORMALIZE_PASS')


def assembly():
    fixtures()
    result = run(['Trinity', '--no_version_check', '--seqType', 'fq', '--max_memory', '1G',
                  '--left=left.fq', '--right=right.fq', '--CPU=1', '--output', 'trinity_out'])
    text = result.stdout + result.stderr
    assert 'salmon-based expression filtering of the final assembly failed' not in text
    assert 'salmon_runner.pl' in text
    output = Path('trinity_out.Trinity.fasta')
    assert output.stat().st_size > 600 and '>TRINITY_' in output.read_text()
    assert Path(str(output)+'.gene_trans_map').stat().st_size > 0
    quants = list(Path('trinity_out').rglob('salmon_outdir/quant.sf'))
    assert quants and all(q.stat().st_size > 40 for q in quants)
    assert any(sum(float(line.split('\t')[4]) for line in q.read_text().splitlines()[1:]) > 0 for q in quants)
    print('TRINITY_ASSEMBLY_SALMON_PASS')


def checkpoint():
    program = '''use strict; use warnings; use lib "/opt/trinity/PerlLib"; use Pipeliner;
my $p = new Pipeliner();
$p->add_commands(new Command("printf recovered > result.txt; printf x >> runs.txt", "done.ok", undef, "result.txt"));
$p->run();
'''
    Path('checkpoint.pl').write_text(program)
    run(['perl', 'checkpoint.pl'])
    assert Path('result.txt').read_text() == 'recovered'
    run(['perl', 'checkpoint.pl'])
    assert Path('runs.txt').read_text() == 'x'
    Path('result.txt').write_text('')
    result = run(['perl', 'checkpoint.pl'])
    assert 'missing or empty' in result.stderr
    assert Path('runs.txt').read_text() == 'xx'
    assert Path('result.txt').read_text() == 'recovered'
    run(['perl', 'checkpoint.pl'])
    assert Path('runs.txt').read_text() == 'xx'
    Path('failure.pl').write_text('use lib "/opt/trinity/PerlLib"; use Pipeliner; Pipeliner::process_cmd("sh -c \'exit 23\'");')
    failed = subprocess.run(['perl', 'failure.pl'], text=True, capture_output=True)
    assert failed.returncode != 0 and '[exit code 23]' in failed.stderr
    print(failed.stderr, file=sys.stderr)
    print('TRINITY_CHECKPOINT_RECOVERY_PASS')


def matrix():
    for name, count in [('sample_b', 2), ('sample_a', 3)]:
        Path(name).mkdir()
        Path(name, 'quant.sf').write_text('Name\tLength\tEffectiveLength\tTPM\tNumReads\n'
                                        f'tx_z\t100\t80\t500000\t{count}\n'
                                        f'tx_a\t100\t80\t500000\t{count}\n')
    run(['abundance_estimates_to_matrix.pl', '--est_method', 'salmon', '--cross_sample_norm', 'none',
         '--gene_trans_map', 'none', '--name_sample_by_basedir', '--out_prefix', 'matrix', 'sample_b/quant.sf', 'sample_a/quant.sf'])
    text = Path('matrix.isoform.counts.matrix').read_text()
    assert text.splitlines() == ['\tsample_b\tsample_a', 'tx_a\t2\t3', 'tx_z\t2\t3']
    missing = subprocess.run(['abundance_estimates_to_matrix.pl', '--est_method'], text=True, capture_output=True)
    assert missing.returncode != 0 and not Path('salmon.isoform.counts.matrix').exists()
    original = Path('matrix.isoform.counts.matrix').read_bytes()
    Path('sample_a/quant.sf').write_text('Name\tLength\tEffectiveLength\tTPM\tNumReads\n'
                                       'different_tx\t100\t80\t1000000\t3\n')
    mismatch = subprocess.run(['abundance_estimates_to_matrix.pl', '--est_method', 'salmon',
                              '--cross_sample_norm', 'none', '--gene_trans_map', 'none', '--name_sample_by_basedir',
                              '--out_prefix', 'mismatch', 'sample_b/quant.sf', 'sample_a/quant.sf'],
                             text=True, capture_output=True, timeout=30)
    sys.stdout.write(mismatch.stdout)
    sys.stderr.write(mismatch.stderr)
    assert mismatch.returncode != 0
    assert 'not all quantification files report the same set of features' in mismatch.stderr
    assert Path('matrix.isoform.counts.matrix').read_bytes() == original
    assert all(p.stat().st_size == 0 for p in Path('.').glob('mismatch.*.matrix'))
    print('TRINITY_MATRIX_PASS')


if __name__ == '__main__':
    action = sys.argv[1]
    functions = dict(identity=identity, help=help_check, fixtures=fixtures, stats=stats,
                     normalize=normalize, assembly=assembly, checkpoint=checkpoint, matrix=matrix)
    if action == 'fixtures':
        fixtures()
    elif action in ('identity', 'help'):
        functions[action]()
    else:
        with tempfile.TemporaryDirectory(prefix='taf-trinity-') as scratch:
            os.chdir(scratch)
            functions[action]()
