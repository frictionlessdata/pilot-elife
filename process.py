import json
import os
import glob
import sys

files = glob.glob('articles/*.json')


def check_file_type(path):
    name, ext = os.path.splitext(path)
    return ext.lower().strip('.') in ('csv', 'xls', 'xlsx')


def check_content(content, data_files):
    for subcontent in content['content']:
        if 'assets' in subcontent:
            for asset in subcontent['assets']:
                if 'sourceData' in asset:
                    for data_file in asset['sourceData']:
                        if check_file_type(data_file['filename']):
                            data_files.append({
                                'filename': data_file['filename'],
                                'uri': data_file['uri'],
                                'type': 'figure'
                            })
        if 'content' in subcontent:
            check_content(subcontent)


def extract_file_urls():

    out = []
    total_articles = 0

    for _file in files:
        with open(_file, 'r') as f:
            article = json.load(f)

            data_files = []

            if article.get('body'):
                for content in article['body']:
                    check_content(content, data_files)

            for data_file in article.get('additionalFiles', []):
                if check_file_type(data_file['filename']):
                    data_files.append({
                        'filename': data_file['filename'],
                        'uri': data_file['uri'],
                        'type': 'additional'
                    })

            if data_files:
                out.append({
                    'id': article['id'],
                    'doi': article['doi'],
                    'title': article['title'],
                    'files': data_files,
                })
        total_articles += 1

    number_of_files = []
    type_counts = {'csv': 0, 'xls': 0, 'xlsx': 0}
    for item in out:
        number_of_files.append(len(item['files']))
        for _file in item['files']:
            name, ext = os.path.splitext(_file['uri'])
            type_counts[ext.strip('.')] += 1

    with open('output/output.json', 'w') as f:
        json.dump(out, f, indent=2)
        msg = '''
Done. {total} articles, {with_data} articles with data.
Average data files per article: {average:.2f}
File type counts: {counts}
    '''.format(
            total=total_articles,
            with_data=len(out),
            average=sum(number_of_files)/len(out),
            counts=type_counts,
        )

        print(msg)


def validate_urls():
    pass


USAGE = '''
python articles.py [extract|validate]
'''

if __name__ == '__main__':

    if len(sys.argv) != 2 or sys.argv[1] not in ('extract', 'validate'):
        print(USAGE)
        sys.exit(1)

    if sys.argv[1] == 'extract':
        extract_file_urls()
    elif sys.argv[1] == 'validate':
        validate_urls()
