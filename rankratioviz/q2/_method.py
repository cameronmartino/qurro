# ----------------------------------------------------------------------------
# Copyright (c) 2018--, rankratioviz development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------
import os
import json
import qiime2
import skbio
import biom
import q2templates
from shutil import copyfile
from rankratioviz.generate import process_input, gen_rank_plot, gen_sample_plot


def plot(output_dir: str, abundance_table: biom.Table,
         ranks: skbio.OrdinationResults, sample_metadata: qiime2.Metadata,
         feature_metadata: qiime2.Metadata, category: str) -> None:

    # get data
    U, V, loaded_table = process_input(
        ranks,
        abundance_table,
        feature_metadata.to_dataframe()
    )
    # We can't "subscript" Q2 Metadata types, so we have to convert this to a
    # dataframe before working with it
    df_sample_metadata = sample_metadata.to_dataframe()
    rank_plot_chart = gen_rank_plot(U, V, 0)
    sample_plot_json = gen_sample_plot(
        loaded_table,
        df_sample_metadata,
        category
    )
    # make dir
    os.makedirs(output_dir, exist_ok=True)
    # copy files for viz
    # TODO: this is slightly unsafe -- if no .html file is found in data/, then
    # this will fail. Solution is to define index = None first, and then after
    # the loop double-check that index isn't None anymore. If it still is then
    # we can fail gracefully with an explanation.
    loc_ = os.path.dirname(os.path.realpath(__file__))
    support_files_loc = os.path.join(loc_, '..', 'support_files')
    for file_ in os.listdir(support_files_loc):
        if file_ != '.DS_Store':
            copyfile(
                os.path.join(support_files_loc, file_),
                os.path.join(output_dir, file_)
            )
        if '.html' in file_:
            index = os.path.join(output_dir, file_)

    # write JSON files to the output directory
    rank_plot_loc = os.path.join(output_dir, "rank_plot.json")
    sample_plot_loc = os.path.join(output_dir, "sample_logratio_plot.json")
    rank_plot_chart.save(rank_plot_loc)
    with open(sample_plot_loc, "w") as jfile:
        json.dump(sample_plot_json, jfile)
    # render the visualization using q2templates.render().
    # TODO: do we need to specify plot_name in the context in this way? I'm not
    # sure where it is being used in the first place, honestly.
    plot_name = output_dir.split('/')[-1]
    q2templates.render(index, output_dir, context={'plot_name': plot_name})
