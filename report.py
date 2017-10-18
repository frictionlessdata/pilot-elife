import ijson
import csv

limit_per_error_type = 0
limit_per_error_type_global = 0
error_counts_global = {}
error_counts = {}
with open('output/article_reports.json', 'r') as f:
    with open('output/errors_files.csv', 'w') as fw:
        writer = csv.DictWriter(fw, fieldnames=[
            'article', 'file', 'error_code', 'error_message'])
        writer.writeheader()
        articles = ijson.items(f, 'item')
        for article in articles:
            if article['report']['valid']:
                continue
            tables = article['report']['tables']
            for table in tables:

                error_counts = {}
                if table['valid']:
                    continue
                for error in table['errors']:
                    if not error['code'] in error_counts_global:
                        error_counts_global[error['code']] = 0
                    error_counts_global[error['code']] += 1

                    if not error['code'] in error_counts:
                        error_counts[error['code']] = 0
                    error_counts[error['code']] += 1


                    if (limit_per_error_type and limit_per_error_type_global) and (
                            error_counts[error['code']] > limit_per_error_type or
                            error_counts_global[error['code']] > limit_per_error_type_global):
                        continue

                    writer.writerow({
                        'article': 'https://elifesciences.org/articles/{id}'.format(id=article['id']),
                        'file': table['source'],
                        'error_code': error['code'],
                        'error_message': error['message']})
