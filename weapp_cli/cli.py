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
    if sex == '1':
        data['inputs']['sex'] = sample.data['inputs']['sex']
    if age == '1':
        data['inputs']['age'] = sample.data['inputs']['age']
    if ancestry == '1':
        data['inputs']['ancestry'] = sample.data['inputs']['ancestry']
    if haplogroup == '1':
        data['inputs']['haplogroup'] = sample.data['inputs']['haplogroup']
    if genome == '1':
        data['inputs']['data'] = sample.data['inputs']['data']
    elif rsid_file != '':
        rsids_fh = open(rsid_file, 'r')
        rsids = rsids_fh.readline().strip().lower().split(',')
        rsids_fh.close()
        user_genome = process_raw_genome_data(sample.data['inputs'])
        for rsid in rsids:
            try:
                data['inputs'][rsid.upper()] = user_genome[rsid]['genotype']
            except:
                click.echo(rsid + ' does not exist, ignored')

    return json.dumps(data, indent=4)


@click.group()
def cli():
    pass


@cli.command()
@click.option('--project', prompt='Project Name', default='weapp-project',
              help='Name of the project')
@click.option('--language', prompt='Language to Use', default='python27',
              type=click.Choice(['python27', 'r']), help='Language of the App')
@click.option('--sex', prompt='Require Sex', type=click.Choice(['0', '1']),
              default='0', help='Whether to require sex data')
@click.option('--age', prompt='Require Age', type=click.Choice(['0', '1']),
              default='0', help='Whether to require age data')
@click.option('--ancestry', prompt='Require Ancestry Composition',
              type=click.Choice(['0', '1']), default='0',
              help='Whether to require ancestry composition')
@click.option('--haplogroup', prompt='Require Haplogroup',
              type=click.Choice(['0', '1']), default='0',
              help='Whether to require haplogroup data')
@click.option('--genome', prompt='Require Whole Genome Data',
              type=click.Choice(['0', '1']), default='0',
              help='Whether to require whole genome data')
@click.option('--rsid_file', prompt='RSID List File', default='',
              help='A list file with rsids required separated by comma')
def init(project, language, sex, age, ancestry, haplogroup, genome, rsid_file):
    work_directory = os.getcwd()
    lib_directory = os.path.split(os.path.abspath(__file__))[0]
    project_directory = work_directory + '/' + project
    project_data_directory = project_directory + '/data'

    click.echo('Initializing the project...')

    if(os.path.isdir(project_directory)):
        click.echo('Aborted. Project folder already exists!')
        exit()

    if genome == '1' and rsid_file != '':
        click.echo('Required whole genome, reguired SNP data will be ignored.')

    if genome == '0' and rsid_file != '':
        if not os.path.isfile(rsid_file):
            click.echo('Aborted. RSID list file does not exist!')
            exit()

    click.echo('Generating scaffold scripts...')

    os.makedirs(project_directory)
    os.makedirs(project_data_directory)

    meta = {'project': project, 'language': language}
    meta_file = open(project_directory + '/.weapp', 'w')
    meta_file.write(json.dumps(meta, indent=4))
    meta_file.close()

    if language == 'python27':
        copy2(lib_directory + '/file_templates/requirements.txt', project_directory)
        copy2(lib_directory + '/file_templates/wegene_utils.py', project_directory)
        copy2(lib_directory + '/file_templates/main.py', project_directory)
        copytree(lib_directory + '/indexes', project_directory + '/indexes')
    elif language == 'r':
        copy2(lib_directory + '/file_templates/pacman.R', project_directory)
        copy2(lib_directory + '/file_templates/wegene_utils.R', project_directory)
        copy2(lib_directory + '/file_templates/main.R', project_directory)
        copytree(lib_directory + '/indexes', project_directory + '/indexes')

    click.echo('Generating test data...')

    data_file = open(project_data_directory + '/data.json', 'w')
    data_file.write(generate_test_data(sex, age, ancestry, haplogroup,
                                       genome, rsid_file, 'wegene_affy_2'))
    data_file.close()


@cli.command()
def test():
    if not os.path.isfile('.weapp'):
        click.echo('Aborted. Not a weapp project folder!')
        exit()
    else:
        click.echo('Testing your weapp using the generated testing data...\n')
        with open('.weapp') as meta_file:
            meta = json.load(meta_file)
        language = meta['language']
        p1 = subprocess.Popen(['cat', './data/data.json'],
                              stdout=subprocess.PIPE)
        if language == 'python27':
            p2 = subprocess.Popen(['python', 'main.py'],
                                  stdin=p1.stdout, stdout=subprocess.PIPE)
        elif language == 'r':
            p2 = subprocess.Popen(['Rscript', 'main.R'],
                                  stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()

        click.echo('WeApp Outputs: ')
        if p2.stdout is not None:
            click.echo(p2.stdout.read() + '\n')
        else:
            click.echo('None\n')

        click.echo('WeApp Errors: ')
        if p2.stderr is not None:
            click.echo(p2.stderr.read() + '\n')
        else:
            click.echo('None\n')


@cli.command()
def package():
    if not os.path.isfile('.weapp'):
        click.echo('Aborted. Not a weapp project folder!')
        exit()
    else:
        click.echo('Archiving the weapp...')
        with open('.weapp') as meta_file:
            meta = json.load(meta_file)
        archive_name = meta['project'] + '.zip'
        zipf = zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED)
        for dirname, subdirs, files in os.walk('.'):
            if dirname != './data' and dirname != './indexes':
                zipf.write(dirname)
                for filename in files:
                    if filename != archive_name:
                        zipf.write(os.path.join(dirname, filename))
            else:
                click.echo('Ignored folders for local testing: ' + dirname)
        zipf.close()
        click.echo('Archiving completed!')


if __name__ == '__main__':
    cli()
