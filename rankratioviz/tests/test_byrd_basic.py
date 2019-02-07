import os
from rankratioviz import generate
from rankratioviz.tests import testing_utilities


def test_matchdf():
    """Tests rankratioviz.generate.matchdf()."""


def test_byrd():
    """Tests the JSON generation on the Byrd et al. 2017 dataset."""

    test_input_dir = os.path.join("data", "byrd")
    test_output_dir = os.path.join("rankratioviz", "tests", "output", "byrd")

    input_rank_loc = os.path.join(test_input_dir, "beta.csv")
    rank_json_loc = os.path.join(test_output_dir, "rank_plot.json")
    # Super basic initial "test." This just makes sure that we don't get any
    # errors. (I'll make this actually test stuff soon.)
    generate.run_script([
        "-r", input_rank_loc,
        "-t", os.path.join(test_input_dir, "byrd_skin_table.biom"),
        "-m", os.path.join(test_input_dir, "byrd_metadata.txt"),
        "-d", test_output_dir
    ])

    # We use the ranks contained in column 3 (0-indexed) because they
    # correspond to the log(PostFlare/Flare) + K ranks: the column name for
    # this in beta.csv is "C(Timepoint, Treatment('F'))[T.PF]".
    # When adapting this test to other datasets/rank files, you'll need to
    # adjust this parameter accordingly.
    testing_utilities.validate_rank_plot_json(input_rank_loc, rank_json_loc, 3)
    # TODO validate sample scatterplot JSON
