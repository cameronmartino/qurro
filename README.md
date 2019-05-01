# rankratioviz
[![Build Status](https://travis-ci.org/fedarko/rankratioviz.svg?branch=master)](https://travis-ci.org/fedarko/rankratioviz) [![codecov](https://codecov.io/gh/fedarko/rankratioviz/branch/master/graph/badge.svg)](https://codecov.io/gh/fedarko/rankratioviz)

(Name subject to change.)

rankratioviz visualizes the output from a tool like
[songbird](https://github.com/biocore/songbird) or
[DEICODE](https://github.com/biocore/DEICODE). It facilitates viewing
a __"ranked"__ plot of features (generally taxa or metabolites) alongside
a scatterplot showing the __log ratios__ of selected feature counts within samples.

rankratioviz can be used standalone (as a Python 3 script that generates a
folder containing a HTML/JS/CSS visualization) or as a
[QIIME 2](https://qiime2.org/) plugin (that generates a QZV file that can be
visualized at [view.qiime2.org](https://view.qiime2.org/) or by using
`qiime tools view`).

rankratioviz should work with most modern web browsers. Firefox or Chrome are
recommended.

rankratioviz is still being developed, so backwards-incompatible changes might
occur. If you have any questions, feel free to contact the development team at
[mfedarko@ucsd.edu](mailto:mfedarko@ucsd.edu).

## Screenshot and Demo

![Screenshot](https://github.com/fedarko/rankratioviz/blob/master/screenshots/redsea_data.png)

This visualization (which uses some of the
[Red Sea metagenome data](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5315489/), with ranks generated by
[songbird](https://github.com/biocore/songbird/)) can be viewed online [here](https://view.qiime2.org/?src=https%3A%2F%2Fwww.dropbox.com%2Fs%2Frrucoomonr1037r%2Fredsea_20190427.qzv).

## Installation and Usage

The following command will install the most up-to-date version of rankratioviz:

```
pip install git+https://github.com/fedarko/rankratioviz.git
```

### Temporary Caveat

**Please make sure that your sample metadata fields do not contain any period or
square bracket characters (`.[]`).** This is due to Vega-Lite's special treatment
of these characters. (Eventually rankratioviz should be able to handle this
accordingly, but in the meantime this is a necessary fix.) See
[this issue](https://github.com/fedarko/rankratioviz/issues/66) for context.

### Tutorials

Examples of using rankratioviz (both inside and outside of QIIME 2) are
available in rankratioviz' example Jupyter notebooks, which are located
[here](https://github.com/fedarko/rankratioviz/tree/master/example_notebooks):
- [**`deicode_example.ipynb`**](https://github.com/fedarko/rankratioviz/blob/master/example_notebooks/DEICODE_sleep_apnea/deicode_example.ipynb)
  demonstrates using [DEICODE](https://github.com/biocore/DEICODE) and then using rankratioviz to visualize DEICODE's output.
- [**`songbird_example.ipynb`**](https://github.com/fedarko/rankratioviz/blob/master/example_notebooks/songbird_red_sea/songbird_example.ipynb)
  demonstrates using [songbird](https://github.com/biocore/songbird) and then using rankratioviz to visualize songbird's output.

## Linked visualizations
These two visualizations (the rank plot and sample scatterplot) are linked [1]:
selections in the rank plot modify the scatterplot of samples, and
modifications of the sample scatterplot that weren't made through the rank plot
trigger an according update in the rank plot.

To elaborate on that: clicking on two taxa in the rank plot sets a new
numerator taxon (determined from the first-clicked taxon) and a new denominator
taxon (determined from the second-clicked taxon) for the abundance log ratios
in the scatterplot of samples.

You can also run textual queries over the various taxa definitions, in order to
create more complicated log ratios
(e.g. "the log ratio of the combined abundances of all
taxa with rank X over the combined abundances of all taxa with rank Y").
Although this method doesn't require you to manually select taxa on the rank
plot, the rank plot is still updated to indicate the taxa used in the log
ratios.

## Acknowledgements

### Dependencies

Code files for the following projects are distributed within
`rankratioviz/support_file/vendor/`.
See the `dependency_licenses/` directory for copies of these software projects'
licenses (each of which includes a respective copyright notice).
- [Vega](https://vega.github.io/vega/)
- [Vega-Lite](https://vega.github.io/vega-lite/)
- [Vega-Embed](https://github.com/vega/vega-embed)
- [RequireJS](https://requirejs.org/)

The following software projects are required for rankratioviz's python code
to function, although they are not distributed with rankratioviz (and are
instead installed alongside rankratioviz).
- [Python 3](https://www.python.org/) (a version of at least 3.5 is required)
- [Altair](https://altair-viz.github.io/)
- [biom-format](http://biom-format.org/)
- [click](https://palletsprojects.com/p/click/)
- [pandas](https://pandas.pydata.org/)
- [scikit-bio](http://scikit-bio.org/)

### Testing Dependencies

For python testing/style checking, rankratioviz uses
[pytest](https://docs.pytest.org/en/latest/),
[pytest-cov](https://github.com/pytest-dev/pytest-cov),
[flake8](http://flake8.pycqa.org/en/latest/), and
[black](https://github.com/ambv/black).

For JavaScript testing/style checking, rankratioviz uses
[Mocha](https://mochajs.org/), [Chai](https://www.chaijs.com/),
[mocha-headless-chrome](https://github.com/direct-adv-interfaces/mocha-headless-chrome),
[nyc](https://github.com/istanbuljs/nyc), [jshint](https://jshint.com/),
and [prettier](https://prettier.io/).

rankratioviz also uses [Travis-CI](https://travis-ci.org/) and
[Codecov](https://codecov.io/).

### Data Sources

The test data located in `rankratioviz/tests/input/byrd/` is from
[this repository](https://github.com/knightlab-analyses/reference-frames).
This data, in turn, originates from Byrd et al.'s 2017 study on atopic
dermatitis [2].

The test data located in `rankratioviz/tests/input/sleep_apnea/`
(and in `example_notebooks/DEICODE_sleep_apnea/input/`)
is from [this Qiita study](https://qiita.ucsd.edu/study/description/10422),
which is associated with Tripathi et al.'s 2018 study on sleep apnea [4].

Lastly, the data located in `rankratioviz/tests/input/red_sea`
(and in `example_notebooks/songbird_red_sea/input/`) was
taken from songbird's GitHub repository in its
[`data/redsea/`](https://github.com/biocore/songbird/tree/master/data/redsea)
folder, and is associated with
[this paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5315489/) [3].

### Special Thanks

The design of rankratioviz was strongly inspired by
[EMPeror](https://github.com/biocore/emperor) and
[q2-emperor](https://github.com/qiime2/q2-emperor/), along with
[DEICODE](https://github.com/biocore/DEICODE). A big shoutout to
Yoshiki Vázquez-Baeza for his help in planning this project, as well as to
Cameron Martino for a ton of work on getting the code in a distributable state
(and making it work with QIIME 2). Thanks also to Jamie Morton, who wrote the
original code for producing rank plots from which this is derived.

## References

[1] Becker, R. A. & Cleveland, W. S. (1987). Brushing scatterplots. _Technometrics, 29_(2), 127-142. (Section 4.1 in particular talks about linking visualizations.)

[2] Byrd, A. L., Deming, C., Cassidy, S. K., Harrison, O. J., Ng, W. I., Conlan, S., ... & NISC Comparative Sequencing Program. (2017). Staphylococcus aureus and Staphylococcus epidermidis strain diversity underlying pediatric atopic dermatitis. _Science translational medicine, 9_(397), eaal4651.

[3] Thompson, L. R., Williams, G. J., Haroon, M. F., Shibl, A., Larsen, P.,
Shorenstein, J., ... & Stingl, U. (2017). Metagenomic covariation along densely
sampled environmental gradients in the Red Sea. _The ISME journal, 11_(1), 138.

[4] Tripathi, A., Melnik, A. V., Xue, J., Poulsen, O., Meehan, M. J., Humphrey, G., ... & Haddad, G. (2018). Intermittent hypoxia and hypercapnia, a hallmark of obstructive sleep apnea, alters the gut microbiome and metabolome. _mSystems, 3_(3), e00020-18.

## License

This tool is licensed under the [BSD 3-clause license](https://en.wikipedia.org/wiki/BSD_licenses#3-clause_license_(%22BSD_License_2.0%22,_%22Revised_BSD_License%22,_%22New_BSD_License%22,_or_%22Modified_BSD_License%22)).
Our particular version of the license is based on [scikit-bio](https://github.com/biocore/scikit-bio)'s [license](https://github.com/biocore/scikit-bio/blob/master/COPYING.txt).
