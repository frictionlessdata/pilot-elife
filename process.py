import json
import os
import glob
import sys
import datetime

from goodtables import Inspector

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

    with open('output/article_files.json', 'w') as f:
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
    with open('output/article_files.json', 'r') as f:
        articles = json.load(f)

    status_counts = {'valid': 0, 'invalid': 0}
    files_count = 0
    with open('output/article_reports.json', 'w') as f:
        f.write('[\n')
        for index, article in enumerate(articles):

            sources = [{'source': _file['uri']} for _file in article['files']]

            inspector = Inspector()
            report = inspector.inspect(sources, preset='nested')

            out = article.copy()
            out['report'] = report

            if report['valid']:
                status_counts['valid'] += 1
            else:
                status_counts['invalid'] += 1
            files_count += len(sources)

            def datetime_handler(x):
                if isinstance(x, datetime.datetime):
                    return x.isoformat()

            f.write(
                json.dumps(out, indent=2, default=datetime_handler) + ',\n')
            print('Validated article {} of {}'.format(index, len(articles)))

            del out

        f.write('\n]')
    msg = '''
Done. {total} articles validated, {files_count} files.
Articles with valid files: {valid}
Articles with invalid files: {invalid}
    '''.format(
            total=len(articles),
            files_count=files_count,
            valid=status_counts['valid'],
            invalid=status_counts['invalid'],
    )

    print(msg)


def report_stats():

    status_counts = {'valid': 0, 'invalid': 0}
    error_counts = {}
    with open('output/article_reports.json', 'r') as f:
        articles = json.load(f)
        for article in articles:
            if article['report']['valid']:
                status_counts['valid'] += 1
                continue
            else:
                status_counts['invalid'] += 1

            for table in article['report']['tables']:
                if table['valid']:
                    continue

                for error in table['errors']:
                    if error['code'] not in error_counts:
                        error_counts[error['code']] = 0

                    error_counts[error['code']] += 1

    msg = '''
Articles with valid files: {valid}
Articles with invalid files: {invalid}
Error types: {error_types}
    '''.format(
            valid=status_counts['valid'],
            invalid=status_counts['invalid'],
            error_types=error_counts
    )

    print(msg)


USAGE = '''
python articles.py [extract|validate|stats]
'''

if __name__ == '__main__':

    if len(sys.argv) != 2 or sys.argv[1] not in ('extract', 'validate', 'stats'):
        print(USAGE)
        sys.exit(1)

    if sys.argv[1] == 'extract':
        extract_file_urls()
    elif sys.argv[1] == 'validate':
        validate_urls()
    elif sys.argv[1] == 'stats':
        report_stats()
