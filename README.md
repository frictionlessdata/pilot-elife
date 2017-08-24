# eLife - GoodTables 

Scripts and data for the eLife / Goodtables pilot

Usage:

* `python articles.py ids`: Creates a file names `article_ids.txt` with the ids extracted from the file names in [this repo](https://github.com/elifesciences/elife-article-xml). Requirest a `GITHUB_TOKEN` env var.
* `python articles.py download`: Downloads a JSON file for each article via the [eLife API]() and stores it in the `articles` folder.
* `python process.py extract`: Extract file URLs from the article metadata files and store them in `output/article_files.json`. The JSON file is an array with each object having the following structure:

    ```json
    { 
      "id": "16072",
      "doi": "10.7554/eLife.16072",
      "title": "CELF RNA binding proteins promote axon regeneration in <i>C. elegans</i> and mammals through alternative splicing of Syntaxins",
      "files": [
        {
          "type": "additional",
          "uri": "https://cdn.elifesciences.org/articles/16072/elife-16072-supp1-v2.xlsx",
          "filename": "elife-16072-supp1-v2.xlsx"
        },
        {
          "type": "additional",
          "uri": "https://cdn.elifesciences.org/articles/16072/elife-16072-supp4-v2.xlsx",
          "filename": "elife-16072-supp4-v2.xlsx"
        },
        {
          "type": "additional",
          "uri": "https://cdn.elifesciences.org/articles/16072/elife-16072-supp7-v2.xlsx",
          "filename": "elife-16072-supp7-v2.xlsx"
        }
      ]
    }
    ```

* `python process.py validate`: Run the goodtables validation process against each article. Results are stored in `output/article_reports.json`, which has the same structure as above but with an extra `report` key for each article. The `report` key contains a standard goodtables report, eg:

    ```json
	{
		"table-count": 1,
		"valid": false,
		"error-count": 1,
		"time": 0.527,
		"warnings": [],
		"tables": [
		  {
			"source": "https://cdn.elifesciences.org/articles/05871/elife-05871-supp1-v1.xlsx",
			"row-count": 60,
			"valid": false,
			"headers": null,
			"time": 0.526,
			"errors": [
			  {
				"code": "blank-row",
				"column-number": null,
				"row-number": 2,
				"message": "Row 2 is completely blank",
				"row": [
				  null,
				  null,
				  null,
				  null,
				  null,
				  null,
				  null,
				  null,
				  null,
				  null,
				  null
				]
			  }
			],
			"error-count": 1
		  }
		]
	  }

    ```

* `python process.py stats`: Show some basic stats on all the generated reports (articles with valid files, Articles with invalid files and error types).
