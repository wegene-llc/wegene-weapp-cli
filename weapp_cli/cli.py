# -*- coding: utf-8 -*-

import click
import os
import json
import zipfile
import wget
import subprocess
from shutil import copy2, copytree
import markdown
import platform

from weapp_cli.sample import data as sample_data
from weapp_cli.wegene_utils import process_raw_genome_data


def generate_test_data(sex, age, ancestry, haplogroup,
                       genome, rsid_file, array_format, extended_file=''):
    data = {'inputs': {'format': array_format}}
    if sex == 'y':
        data['inputs']['sex'] = sample_data['inputs']['sex']
    if age == 'y':
        data['inputs']['age'] = sample_data['inputs']['age']
    if ancestry == 'y':
        data['inputs']['ancestry'] = sample_data['inputs']['ancestry']
    if haplogroup == 'y':
        data['inputs']['haplogroup'] = sample_data['inputs']['haplogroup']
    if genome == 'y':
        data['inputs']['data'] = sample_data['inputs']['data']
    elif rsid_file != '':
        rsids_fh = open(rsid_file, 'r')
        rsids = rsids_fh.readlines()
        rsids = list(map(lambda rsid: rsid.strip().lower(), rsids))
        rsids_fh.close()
        user_genome = process_raw_genome_data(sample_data['inputs'])
        if extended_file:
            extended_fh = open(extended_file, 'r')
            extended_data_lines = extended_fh.readlines()
            for line in extended_data_lines:
                rs, chromosome, pos, genotype = line.strip().split('\t')
                if rs in rsids:
                    user_genome[rs] = {
                        'genotype': genotype,
                        'chromosome': chromosome,
                        'position': pos
                    }
            extended_fh.close()
        for rsid in rsids:
            try:
                data['inputs'][rsid.upper()] = user_genome[rsid]['genotype']
            except:
                click.echo(click.style(rsid + ' does not exist, ignored',
                                       fg='yellow'))

    return json.dumps(data)


@click.group()
def cli():
    pass


@cli.command()
@click.option('--project', prompt='Project Name', default='weapp-project',
              help='Name of the project')
@click.option('--language', prompt='Language to Use', default='python27',
              type=click.Choice(['python27', 'python3', 'r']), help='Language of the App')
@click.option('--sex', prompt='Require Sex', type=click.Choice(['y', 'n']),
              default='y', help='Whether to require sex data')
@click.option('--age', prompt='Require Age', type=click.Choice(['y', 'n']),
              default='y', help='Whether to require age data')
@click.option('--ancestry', prompt='Require Ancestry Composition',
              type=click.Choice(['y', 'n']), default='y',
              help='Whether to require ancestry composition')
@click.option('--haplogroup', prompt='Require Haplogroup',
              type=click.Choice(['y', 'n']), default='y',
              help='Whether to require haplogroup data')
@click.option('--genome', prompt='Require Whole Genome Data',
              type=click.Choice(['y', 'n']), default='y',
              help='Whether to require whole genome data')
@click.option('--rsid_file', prompt='RSID List File', default='',
              help='A list file with rsids required separated by new line')
@click.option('--markdown', prompt='Output In Markdown Format',
              type=click.Choice(['y', 'n']), default='y',
              help='Whether to use markdown for output')
def init(project, language, sex, age, ancestry, haplogroup, genome, rsid_file, markdown):
    work_path = os.getcwd()
    lib_path = os.path.split(os.path.abspath(__file__))[0]
    project_path = work_path + '/' + project
    project_data_path = project_path + '/data'
        
    click.echo(click.style('Initializing the project...', fg='green'))

    if(os.path.isdir(project_path)):
        click.echo(click.style('Aborted. Project folder already exists!',
                               fg='red'))
        exit()

    if genome == 'y' and rsid_file != '':
        click.echo(click.style('Required whole genome ' +
                               'reguired SNP data will be ignored.',
                   fg='yellow'))

    if genome == 'n' and rsid_file != '':
        if not os.path.isfile(rsid_file):
            click.echo(click.style('Aborted. RSID list file does not exist!',
                       fg='red'))
            exit()

    click.echo(click.style('Generating scaffold scripts...', fg='green'))

    os.makedirs(project_path)
    os.makedirs(project_data_path)

    if markdown == 'y':
        markdown = 1
        copy2(lib_path + '/file_templates/html_template.html', project_path)
    else:
        markdown = 0

    meta = {'project': project, 'language': language, 'markdown': markdown}
    meta_file = open(project_path + '/.weapp', 'w')
    meta_file.write(json.dumps(meta, indent=4))
    meta_file.close()

    if language == 'python27':
        copy2(lib_path + '/file_templates/python27/requirements.txt', project_path)
        copy2(lib_path + '/file_templates/python27/wegene_utils.py', project_path)
        copy2(lib_path + '/file_templates/python27/main.py', project_path)
        copytree(lib_path + '/indexes', project_path + '/indexes')
    elif language == 'python3':
        copy2(lib_path + '/file_templates/python3/requirements.txt', project_path)
        copy2(lib_path + '/file_templates/python3/wegene_utils.py', project_path)
        copy2(lib_path + '/file_templates/python3/main.py', project_path)
        copytree(lib_path + '/indexes', project_path + '/indexes')
    elif language == 'r':
        copy2(lib_path + '/file_templates/r/pacman.R', project_path)
        copy2(lib_path + '/file_templates/r/wegene_utils.R', project_path)
        copy2(lib_path + '/file_templates/r/main.R', project_path)
        copytree(lib_path + '/indexes', project_path + '/indexes')

    extended_data_file = ''
    if(os.path.isdir(lib_path + '/extended_data')):
        copytree(lib_path + '/extended_data', project_path + '/extended_data')
        extended_data_file = project_path + '/extended_data/extended_data.dat'

    click.echo(click.style('Generating test data...', fg='green'))

    data_file = open(project_data_path + '/data.json', 'w')
    data_file.write(generate_test_data(sex, age, ancestry, haplogroup,
                                       genome, rsid_file, 'wegene_affy_2',
                                       extended_data_file))
    data_file.close()
    click.echo(click.style('Project Initialization Completed', fg='green'))


@cli.command()
def download_extra():
    extended_data_url = 'http://wegene-upload-prod.oss-cn-hangzhou.aliyuncs.com/sample_data/extended_data.zip'
    click.echo(click.style('Downloading extended data, ' +
                           'please wait...',
               fg='green'))
    lib_path = os.path.split(os.path.abspath(__file__))[0]
    try:
        extended_data_archive = wget.download(extended_data_url, out=lib_path)
        click.echo(click.style('\nDownload completed, unpacking now...',
                   fg='green'))
        zip_file = zipfile.ZipFile(extended_data_archive)
        for names in zip_file.namelist():
            zip_file.extract(names, lib_path)
        zip_file.close()
        click.echo(click.style('Removing temp data...',
                   fg='green'))
        if os.path.exists(extended_data_archive):
            os.remove(extended_data_archive)
        click.echo(click.style('Successfully updated extended data!',
                   fg='green'))
    except Exception:
        click.echo(click.style('Failed to download extended data, ' +
                               'please try again!',
                               fg='red'))

@cli.command()
def test():
    sys_name = platform.system()

    if not sys_name in ['Windows', 'Linux', 'Darwin']:
        click.echo(click.style('Aborted. Unsupported operation system!',
                               fg='red'))
        exit()

    if not os.path.isfile('.weapp'):
        click.echo(click.style('Aborted. Not a weapp project folder!',
                               fg='red'))
        exit()
    else:
        click.echo(click.style('Testing your weapp ' +
                               'using the generated testing data...\n',
                   fg='green'))
        with open('.weapp') as meta_file:
            meta = json.load(meta_file)
        language = meta['language']
        is_markdown = meta['markdown']

        try:
            if sys_name == 'Windows':
                p1 = subprocess.Popen(
                    ['type', 'data\data.json'], stdout=subprocess.PIPE, shell=True)
                if language == 'python27' or language == 'python3':
                    p2 = subprocess.Popen(['python', 'main.py'],
                                        stdin=p1.stdout, stdout=subprocess.PIPE)
                elif language == 'r':
                    p2 = subprocess.Popen(['Rscript', 'main.R'],
                                        stdin=p1.stdout, stdout=subprocess.PIPE)
                console_codec = 'gbk'
            else:
                p1 = subprocess.Popen(
                    ['cat', './data/data.json'], stdout=subprocess.PIPE)
                if language == 'python27':
                    p2 = subprocess.Popen(['python2', 'main.py'],
                                        stdin=p1.stdout, stdout=subprocess.PIPE)
                elif language == 'python3':
                    p2 = subprocess.Popen(['python3', 'main.py'],
                                        stdin=p1.stdout, stdout=subprocess.PIPE)
                elif language == 'r':
                    p2 = subprocess.Popen(['Rscript', 'main.R'],
                                        stdin=p1.stdout, stdout=subprocess.PIPE)
                console_codec = 'UTF-8'
            p1.stdout.close()

            click.echo(click.style('WeApp Outputs: ', fg='green'))
            if p2.stdout is not None and p2.stdout != '':
                if is_markdown:
                    exts = ['markdown.extensions.tables']
                    result = p2.stdout.read().decode(console_codec)
                    result = markdown.markdown(result, extensions=exts)

                    template_file = open(
                        './html_template.html', 'r', encoding='utf-8')
                    html_template = template_file.read()
                    template_file.close()

                    html_file = open('./test_result.html', 'w')
                    html_file.write(html_template.replace('{{RESULTS}}', result))
                    html_file.close()
                else:
                    result = p2.stdout.read().decode(console_codec)
                click.echo(click.style('{}\n'.format(result), fg='yellow'))

                if is_markdown:
                    click.echo(click.style('Note: An HTML file named "test_result.html" is generated for you to test styles\n', fg='green'))
            else:
                click.echo(click.style('None\n', fg='yellow'))

            click.echo(click.style('WeApp Errors: ', fg='green'))
            if p2.stderr is not None:
                click.echo(click.style('{}\n'.format(
                    p2.stderr.read().decode(console_codec)), fg='red'))
            else:
                click.echo(click.style('None\n', fg='yellow'))
        except Exception as e:
            click.echo(click.style('An error has occured during the test: ',
                                   fg='red'))
            click.echo(click.style(str(e), fg='red'))


@cli.command()
def package():
    if not os.path.isfile('.weapp'):
        click.echo(click.style('Aborted. Not a weapp project folder!',
                               fg='red'))
        exit()
    else:
        click.echo(click.style('Archiving the weapp...', fg='green'))
        with open('.weapp') as meta_file:
            meta = json.load(meta_file)
        archive_name = meta['project'] + '.zip'
        zipf = zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED)
        for dirname, subdirs, files in os.walk('.'):
            if dirname not in ['./data', './indexes', './extended_data']:
                zipf.write(dirname)
                for filename in files:
                    if filename not in [archive_name, '.weapp', 'html_template.html', 'test_result.html']:
                        zipf.write(os.path.join(dirname, filename))
            else:
                click.echo(click.style('Ignoring folder for local testing: '
                                       + dirname + '. Do not put your custom '
                                       + 'files under this folder',
                           fg='yellow'))
        zipf.close()
        click.echo(click.style('Archiving completed!', fg='green'))


if __name__ == '__main__':
    cli()
