import click
import os
import json
import zipfile
import subprocess
from shutil import copy2, copytree

import sample
from wegene_utils import process_raw_genome_data


def generate_test_data(sex, age, ancestry, haplogroup,
                       genome, rsid_file, array_format):
    data = {'inputs': {'format': array_format}}
    if sex == 'y':
        data['inputs']['sex'] = sample.data['inputs']['sex']
    if age == 'y':
        data['inputs']['age'] = sample.data['inputs']['age']
    if ancestry == 'y':
        data['inputs']['ancestry'] = sample.data['inputs']['ancestry']
    if haplogroup == 'y':
        data['inputs']['haplogroup'] = sample.data['inputs']['haplogroup']
    if genome == 'y':
        data['inputs']['data'] = sample.data['inputs']['data']
    elif rsid_file != '':
        rsids_fh = open(rsid_file, 'r')
        rsids = rsids_fh.readlines()
        rsids_fh.close()
        user_genome = process_raw_genome_data(sample.data['inputs'])
        for rsid in rsids:
            rsid = rsid.strip().lower()
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
              type=click.Choice(['python27', 'r']), help='Language of the App')
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
def init(project, language, sex, age, ancestry, haplogroup, genome, rsid_file):
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

    meta = {'project': project, 'language': language}
    meta_file = open(project_path + '/.weapp', 'w')
    meta_file.write(json.dumps(meta, indent=4))
    meta_file.close()

    if language == 'python27':
        copy2(lib_path + '/file_templates/requirements.txt', project_path)
        copy2(lib_path + '/file_templates/wegene_utils.py', project_path)
        copy2(lib_path + '/file_templates/main.py', project_path)
        copytree(lib_path + '/indexes', project_path + '/indexes')
    elif language == 'r':
        copy2(lib_path + '/file_templates/pacman.R', project_path)
        copy2(lib_path + '/file_templates/wegene_utils.R', project_path)
        copy2(lib_path + '/file_templates/main.R', project_path)
        copytree(lib_path + '/indexes', project_path + '/indexes')

    click.echo(click.style('Generating test data...', fg='green'))

    data_file = open(project_data_path + '/data.json', 'w')
    data_file.write(generate_test_data(sex, age, ancestry, haplogroup,
                                       genome, rsid_file, 'wegene_affy_2'))
    data_file.close()
    click.echo(click.style('Project Initialization Completed', fg='green'))


@cli.command()
def test():
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

        try:
            p1 = subprocess.Popen(['cat', './data/data.json'],
                                  stdout=subprocess.PIPE)
            if language == 'python27':
                p2 = subprocess.Popen(['python', 'main.py'],
                                      stdin=p1.stdout, stdout=subprocess.PIPE)
            elif language == 'r':
                p2 = subprocess.Popen(['Rscript', 'main.R'],
                                      stdin=p1.stdout, stdout=subprocess.PIPE)
            p1.stdout.close()

            click.echo(click.style('WeApp Outputs: ', fg='green'))
            if p2.stdout is not None:
                click.echo(click.style(p2.stdout.read() + '\n', fg='yellow'))
            else:
                click.echo(click.style('None\n', fg='yellow'))

            click.echo(click.style('WeApp Errors: ', fg='green'))
            if p2.stderr is not None:
                click.echo(click.style(p2.stderr.read() + '\n', fg='red'))
            else:
                click.echo(click.style('None\n', fg='yellow'))
        except Exception as e:
            click.echo(click.style('An error has occured during the test: ',
                                   fg='red'))
            click.echo(click.style(e.stderr, fg='red'))


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
            if dirname != './data' and dirname != './indexes':
                zipf.write(dirname)
                for filename in files:
                    if filename != archive_name and filename != '.weapp':
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
